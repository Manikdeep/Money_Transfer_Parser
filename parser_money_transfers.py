"""Money Transfer Parser"""
import os
import re
import csv
import base_parser
from OCR import colors_dict
# from color_dict import colors_dict

#If cloning from GitHub, make sure you change the file paths for the text files

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
            result.append(i.group())

        #find with S digit and deciaml
        for i in re.finditer(r"\b[S]\d{1,3}(?:,\d{3})*(?:\.\d+)+|\b[S]\d{1,3}(?:,\d{3})*", my_content):         
            result.append(i.group()[1:])

        # find with $ digit and decimal
        for i in re.finditer(r"\$\d{1,}(?:,\d{3})*(?:\.\d+)*|\$\d{1,3}(?:,\d{3})*", my_content):
            result.append(i.group()[1:])
        return result

    def transfer_amount(self, content):
        """return the amounts present in the content"""
        result = []
        add_amounts = []
        content_lower = content.lower()
        count = content.count("Add Cash")
        # some picturs have multiple cash amounts that need to be added up, so this statement checks for that
        if count>2:
            if 'amount' in content_lower:
                the_amount = self.find_money_values(content, result)
                for j, number in enumerate(the_amount):
                    the_amount[j] = self.clean_number(number)
                return [float(max(the_amount))]
            add_amounts = self.find_money_values(content, add_amounts)
            for i, value in enumerate(add_amounts):
                add_amounts[i] = int(value)
            return [sum(add_amounts)]
        # cash amounts after 'watchlist' are invalid
        if 'watchlist' in content_lower:
            end = content_lower.find('watchlist')
            new_content1 = content_lower[:end]
            result = self.find_money_values(new_content1, result)
        # cash amounts before 'total' are invalid
        elif 'total' in content_lower:
            start = content_lower.find('total')
            new_content = content_lower[start:]
            result = self.find_money_values(new_content, result)
        # picture specific check (not encouraged)
        elif 'bortow' in content_lower:
            end = content_lower.find('bortow')
            new_content = content_lower[:end]
            result = self.find_money_values(new_content, result)
        # picture specific check (not encouraged)
        elif 'paypal' in content_lower and 'limits' in content_lower:
            return [" "]
        else:
            result = self.find_money_values(content, result)
        # created a set to hold all the valid cash values that were found in the picture
        final = set()
        if len(result) == 1:
            # if this check is true, the only value shown is bitcoin
            if 'btc' in content.lower():
                list_result = list(result)
                list_result[0] = list_result[0] + " BTC"
                return list_result
        # if there are more than one valid values, the correct value is the max value.
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
        """identifies digital payment type"""
        # checks names before checking most dominant colors
        # For example if the picture says paypal there is no need to check if there is blue.
        dig_type_list = {"paypal", "cash", "coinbase", "portfolio", "asset", "btc", 
            "message", "bnb", "želle", "mobile check", "gift card", "zelle"}
        res = []
        content_lower = content.lower()
        pid = int(transfer.photo_id)
        c_d = colors_dict[pid]
        # picture that displays limits for potential payments is coinbase
        if 'limits' in content_lower and 'paypal' in content_lower:
            return['coinbase']
        for i in dig_type_list:
            if i in content_lower:
                res.append(i)
        if res:
            # if a picture has bitcoin and is blue dominant it is coinbase
            if 'btc' in res:
                j = 0
                while j < len(c_d):
                    if c_d[j+3] > c_d[j+1] and c_d[j+3] > c_d[j+2]:
                        res[0] = "Coinbase"
                        return res
                    j += 4
        if not res:
            # checks for cashapp usernames
            match = re.search(r"\$(?=.*[a-zA-Z])[a-zA-Z\d]{1,20}", content)
            match2 = re.search(r"S(?=.*[a-zA-Z])[a-zA-Z\d]{1,20}", content)
            # checks for emails
            email = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", content)
            username = ""
            # if cashapp username is found, type is cashapp
            if match:
                username = match.group(0)[1:]
                if len(username) > 0 and not username.isnumeric():
                    res.append('Cashapp')
                    return res
                elif match2 and 'today' in content_lower:
                    username = match2.group(0)[1:] 
                    if len(username) > 0 and not username.isnumeric():
                        res.append('Cashapp')
                        return res
            # if an email is found, check if the dominant color is blue. If it is, it's paypal
            if email:
                i = 0
                r, g, b, = None, None, None
                while i < len(c_d):
                    if c_d[i+2] > c_d[i+1] and c_d[i+2] > c_d[i+3]:
                        g = True
                    if c_d[i+3] > c_d[i+1] and c_d[i+3] > c_d[i+2]:
                        b = True
                    if c_d[i+1] > c_d[i+3] and c_d[i+1] > c_d[i+2]:
                        r = True
                    i += 4
                if g and b:
                    res.append('paypal')
                    return res
            # if keywords are not found, check for dominant colors.
            if not res:
                i = 0
                r, g, b, = None, None, None
                while i < len(c_d):
                    if c_d[i+2] > c_d[i+1] and c_d[i+2] > c_d[i+3]:
                        g = True
                    if c_d[i+3] > c_d[i+1] and c_d[i+3] > c_d[i+2]:
                        b = True
                    if c_d[i+1] > c_d[i+3] and c_d[i+1] > c_d[i+2]:
                        r = True
                    i += 4
                # green and blue dominant with 'success' and 'done' is b of a
                if g and b and 'success' in content_lower and 'done' in content_lower:
                    res.append('Bank of America App')
                    return res
                j = 0
                # green dominant is cashapp
                while j < len(c_d):
                    if c_d[j+2] > c_d[j+1] and c_d[j+2] > c_d[j+3]:
                        res.append('CashApp')
                        break
                    j += 4
                if not res:
                    i = 0   
                    # blue dominant is paypal
                    while i < len(c_d):
                        if c_d[i+3] > c_d[i+1] and c_d[i+3] > c_d[i+2]:
                            res.append('Paypal')
                            break
                        i += 4
        return res

    def data_assign_rowby(self, photo_id, date, mt_application, dig_payment, dig_payment_type, amount, official_dep, writer):
        """assigns the values to the excel sheets"""
        writer.writerow([photo_id, date, mt_application, dig_payment, dig_payment_type, amount, official_dep])


if __name__ == '__main__':
    # Update this path with the path to the text files on your system
    # REMOVE FILE AFTER USING IT
    folder_textdoc_path = 'C:/Users/jonat/OneDrive/Documents/EBCS Research/MoneyTransferApps-Textfiles'
    # folder_textdoc_path = 'C:/Users/jonat/OneDrive/Documents/EBCS Research/TestText'
    textdoc_paths = base_parser.get_textdoc_paths(folder_textdoc_path)
    headerList = ['Pic ID', 'Date', 'Money Transfer Application', 'Digital Payments', 
        'Digital Payment Type', 'Amount', 'Official Deposit']
    with open('money_transfers1_file'+'.csv','w', newline='', encoding='utf-8') as f1:
        dw = csv.DictWriter(f1, delimiter=',', fieldnames=headerList)
        dw.writeheader()
        writer=csv.writer(f1, delimiter=',')# lineterminator='\n',
        try:
            for text_doc in textdoc_paths:
                writer=csv.writer(f1, delimiter=',')
                transfer = MoneyTransfers()
                file_name = os.path.basename(text_doc)

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
                # find digital pay type
                digital_pay = transfer.digital_pay_type(text_des)
                if not digital_pay:
                    transfer.dig_payment_type = "No type identified"
                else:
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

                # find transfer amount
                if content:
                    info_amount = transfer.transfer_amount(text_des)
                    if not info_amount:
                        transfer.amount = 0
                    else:
                        if info_amount[0] == " ":
                            transfer.amount = 0
                        else:
                            # if the amount is a string then it is Bitcoin
                            if isinstance(info_amount[0], str):
                                if 'BTC' not in info_amount[0]:
                                    final = " "
                                    for i, value in enumerate(info_amount[0]):
                                        if value == ",":
                                            continue
                                        else:
                                            final += value
                                    transfer.amount = float(final)
                                else:
                                    transfer.amount = info_amount[0]
                            else:
                                transfer.amount = float(info_amount[0])
                transfer.data_assign_rowby(transfer.photo_id, transfer.date, transfer.mt_application,
                transfer.dig_payment, transfer.dig_payment_type,
                transfer.amount, transfer.official_dep, writer)
                del colors_dict[int(photo_id)]
                del_file = 'C:/Users/jonat/OneDrive/Documents/EBCS Research/MoneyTransferApps-Textfiles/' + file_name
                os.remove(del_file)
                picture_file = file_name[0:-3] + "jpg"
                the_picture_file = "C:/Users/jonat/OneDrive/Documents/EBCS Research/MoneyTransferApps-Photos/" + picture_file
                os.remove(the_picture_file)
        except Exception as e:
            print(e)
            print(colors_dict)
