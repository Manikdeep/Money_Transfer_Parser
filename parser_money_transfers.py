import os
import zipcodes
import re
import json
import base_parser
import sys
import csv
# import OCR
from colordict import color_dict
  
# Put 1 in Money Transfer Application and Digital Payments
# Fixed BTC vs USD recognition for normal and 'Total' images
# Fixed Facebook Shop recognition
# Coinbase recognition:
#   if BTC and blue dominant its coinbase, if not BTC and blue dominant, it's paypal
# 5890 is bank of america phone app
#   (check if there is a green, and blue dominant portion of the picture and has the word 'Success')
# BNB Wallet = Binance
# 19974 - Coinbase and Limits means amount is empty
# 20187 - Bank Account so delete it
# 20188 - Bank Account so delete it
# 21267 - Put as giftcard
# 21360 - Coinbase and Limits means amount is empty
# Need Regex for email for paypal recognition 5881
# Fixed Cashapp recognition for usernames that aren't captured properly. 17355
# fixed price for coinbase 'watchlist' pictures 21285
# 22387 wrong price shows up (Check before borrow appears in text)
# remove brackets



class MoneyTransfers:
    """money transfers class"""
    def __init__(self):
        self.date = None
        self.photo_id = None
        self.dig_payment = None
        self.amount = " "
        self.dig_payment_type = None
        self.official_dep = None
        self.mt_application = None

    def clean_number(self, num):
        """removes periods and commas from numbers"""
        clean_num = ""
        try:
            clean_num = float(num)
        except ValueError:
            for i, value in enumerate(num):
                if num[i] == '.' and i != len(num) - 3:
                    continue
                elif num[i] == ',':
                    continue
                clean_num += num[i]
        return clean_num

    def get_date_and_id_from_title(self, title):
        """gets date and id from title"""
        re1 = title.split("@")
        photo_id = re1[0].split("_")[1]
        date = re1[1].split("_")[0]
        return photo_id, date

    def find_money_values(self, my_content, result):
        """finds money value"""
        # find with digit and decimal
        for i in re.finditer(r"\d{1,3}(?:,\d{3})*(?:\.\d+)+", my_content):
            #print(i)
            result.append(i.group())
        #find with S digit and deciaml
        # for i in re.finditer(r"(\b[S][0-9]*\.[0-9]*)|\b[S][0-9]+", content):
        #     print(i.group())
        #     result.add(i.group()[1:])
        for i in re.finditer(r"\b[S]\d{1,3}(?:,\d{3})*(?:\.\d+)+|\b[S]\d{1,3}(?:,\d{3})*", my_content):
            # print(i.group())
            result.append(i.group()[1:])
        # find with $ digit and decimal
        # for i in re.finditer(r"\$\d+(?:\.\d+)?", content):
        #     print(i.group())
        #     result.add(i.group()[1:])
        #for i in re.finditer(r"\$\d{1,3}(?:,\d{3})*(?:\.\d+)+|\$\d{1,3}(?:,\d{3})*", content):
        for i in re.finditer(r"\$\d{1,}(?:,\d{3})*(?:\.\d+)*|\$\d{1,3}(?:,\d{3})*", my_content):
            # print(i.group())
            result.append(i.group()[1:])
        return result

    def transfer_amount(self, content):
        """return the amounts present in the content"""
        result = []
        add_amounts = []
        content_lower = content.lower()
        count = content.count("Add Cash")
        if count>1:
            add_amounts = self.find_money_values(content, add_amounts)
            for i, value in enumerate(add_amounts):
                add_amounts[i] = int(add_amounts[i])
            return [sum(add_amounts)]
        if 'watchlist' in content_lower:
            end = content_lower.find('watchlist')
            new_content1 = content_lower[:end]
            # print(new_content1)
            result = self.find_money_values(new_content1, result)
        elif 'total' in content_lower:
            start = content_lower.find('total')
            new_content = content_lower[start:]
            result = self.find_money_values(new_content, result)
        elif 'bortow' in content_lower:
            end = content_lower.find('bortow')
            new_content = content_lower[:end]
            result = self.find_money_values(new_content, result)
        elif 'paypal' in content_lower and 'limits' in content_lower:
            return [" "]
        else:
            result = self.find_money_values(content, result)
        final = set()
        if len(result) == 1:
            if 'btc' in content.lower():
                list_result = list(result)
                list_result[0] = list_result[0] + " BTC"
                return list_result
        if len(result) > 1:
            for i in result:
                num = self.clean_number(i)
                final.add(float(num))
            if final:
                return [max(final)]
            else:
                return []
        else:
            return result

    def digital_pay_type(self, content):
        """check names before checking most dominant colors
        ie if it says paypal there is no need to check if there is blue.
        for cashapp, check if there is a username ($CashappName) before
        checking for the green color"""
        dig_type_list = {"paypal", "cash", "coinbase", "portfolio", "asset", "btc", "message", "bnb", "želle", "mobile check", "gift card", "zelle"}
        res = []
        content_lower = content.lower()
        pid = int(transfer.photo_id)
        cd = color_dict[pid]
        if 'limits' in content_lower and 'paypal' in content_lower:
            return['coinbase']
        for i in dig_type_list:
            if i in content_lower:
                res.append(i)
        if res:
            if 'btc' in res:
                j = 0
                while j < len(cd):
                    if cd[j+3] > cd[j+1] and cd[j+3] > cd[j+2]:
                        res[0] = "Coinbase"
                        return res
                    j += 4
        if not res:
            # add regular expression check here for cashapp usernames
            match = re.search(r"\$(?=.*[a-zA-Z])[a-zA-Z\d]{1,20}", content)
            match2 = re.search(r"S(?=.*[a-zA-Z])[a-zA-Z\d]{1,20}", content)
            email = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", content)
            username = ""
            if match:
                username = match.group(0)[1:]
                if len(username) > 0 and not username.isnumeric():
                    res.append('Cashapp')
                    return res
                elif match2 and 'today' in content_lower:
                    username = match2.group(0)[1:] #wont work because it also captures 'Success'
                    if len(username) > 0 and not username.isnumeric():
                        res.append('Cashapp')
                        return res
            if email:
                i = 0
                r, g, b, = None, None, None
                while i < len(cd):
                    if cd[i+2] > cd[i+1] and cd[i+2] > cd[i+3]:
                        g = True
                    if cd[i+3] > cd[i+1] and cd[i+3] > cd[i+2]:
                        b = True
                    if cd[i+1] > cd[i+3] and cd[i+1] > cd[i+2]:
                        r = True
                    i += 4
                # print(r, " ", g, " ", b)
                if g and b:
                    # print("this is a b of a")
                    res.append('paypal')
                    return res
            if not res:
                # print(cd)
                i = 0
                r, g, b, = None, None, None
                while i < len(cd):
                    if cd[i+2] > cd[i+1] and cd[i+2] > cd[i+3]:
                        g = True
                    if cd[i+3] > cd[i+1] and cd[i+3] > cd[i+2]:
                        b = True
                    if cd[i+1] > cd[i+3] and cd[i+1] > cd[i+2]:
                        r = True
                    i += 4
                # print(r, " ", g, " ", b)
                if g and b and 'success' in content_lower and 'done' in content_lower:
                    # print("this is a b of a")
                    res.append('Bank of America App')
                    return res
                j = 0
                while j < len(cd):
                    if cd[j+2] > cd[j+1] and cd[j+2] > cd[j+3]:
                        res.append('CashApp')
                        break
                    j += 4
                if not res:
                    i = 0    
                    while i < len(cd):
                        if cd[i+3] > cd[i+1] and cd[i+3] > cd[i+2]:
                            res.append('Paypal')
                            break
                        i += 4
        return res

    def data_assign_rowby(self, photo_id, date, mt_application, dig_payment, dig_payment_type, amount, official_dep, writer):
        """assigns the values to the excel sheets"""
        #num_amount = len(amount)
        # amount = [float(i) for i in amount]
        # amount.sort()
        writer.writerow([photo_id, date, mt_application, dig_payment, dig_payment_type, amount, official_dep])


if __name__ == '__main__':
    folder_textdoc_path = 'C:/Users/jonat/OneDrive/Documents/EBCSphotosText/Textfiles'
    textdoc_paths = base_parser.get_textdoc_paths(folder_textdoc_path)
    headerList = ['Pic ID', 'Date', 'Money Transfer Application', 'Digital Payments', 'Digital Payment Type', 'Amount', 'Official Deposit']
    with open('money_transfers1_file'+'.csv','w', newline='', encoding='utf-8') as f1:
        dw = csv.DictWriter(f1, delimiter=',', fieldnames=headerList)
        dw.writeheader()
        writer=csv.writer(f1, delimiter=',')#lineterminator='\n',
    # for i in np.arange(0,9):
    #     row = data[i]
    #     writer.writerow(row)
  
        for text_doc in textdoc_paths:
            writer=csv.writer(f1, delimiter=',')
            transfer = MoneyTransfers()
            file_name = os.path.basename(text_doc)
            #print(file_name[-34:-4])
            #### parse photo id and date
            photo_id, date = transfer.get_date_and_id_from_title(file_name)
            if photo_id:
                transfer.photo_id = photo_id
            if date:
                transfer.date = date
            print(photo_id)
            with open(text_doc, encoding = "utf-8") as f:
                content = f.readlines()
            if content:
                text_des = content[-1]
            else:
                writer.writerow([transfer.photo_id, transfer.date, "", "", "", ""])
                continue
            #print((text_des).encode('utf-8'))
            #print(text_des)
            digital_pay = transfer.digital_pay_type(text_des)
            #print(digital_pay)
            if digital_pay:
                if digital_pay[0] == "cash":
                    transfer.dig_payment_type = "CashApp"
                elif digital_pay[0] == "portfolio" or digital_pay[0] == "asset":
                    transfer.dig_payment_type = "Coinbase"
                elif digital_pay[0] == "bnb":
                    transfer.dig_payment_type = "Binance"
                elif digital_pay[0] == "message":
                    transfer.dig_payment_type = "Facebook Shop"
                elif digital_pay[0] == "želle" or digital_pay[0] == "zelle":
                    transfer.dig_payment_type = "Zelle"
                else:
                    transfer.dig_payment_type = digital_pay[0]
            transfer.dig_payment = '1'
            transfer.mt_application = '1'

            #parse zipcode and state
            if content:
                info_amount = transfer.transfer_amount(text_des)
                if info_amount[0] == " ":
                    print("im here")
                    transfer.amount = "no amount"
                else:
                    print("im here too")
                    transfer.amount = str(info_amount[0])

            # for i,code in enumerate(check.zipcode):
            #     writer.writerow()

            #print(check.photo_id, check.date, check.bankname, check.zipcode, check.state, check.amount)
            # writer.writerow([check.photo_id, check.date, check.bankname, check.zipcode, check.state, check.amount])
            transfer.data_assign_rowby(transfer.photo_id, transfer.date, transfer.mt_application, transfer.dig_payment, transfer.dig_payment_type, transfer.amount, transfer.official_dep, writer)

        # exit()
        