import os
import zipcodes
import re
import json
import base_parser
import sys
import csv

"""Use Google API to detect colors for each picture to determine if it is a 
   Money Transfer Application(Money Order) or Digital Payment(Cashapp, Zelle, etc.)
   
   2595 has multiple cash amounts that need to be added up.
   2591 - the $4000 is detected but it goes in the excel sheet as 0 for some reason
   
   Regular Expression to check if cashapp username is present"""

class MoneyTransfers:

    def __init__(self):
        self.date = None
        self.photo_id = None
        self.mt_application = None
        self.dig_payment = None
        self.amount = []
        self.dig_payment_type = None
        self.official_dep = None

    def clean_number(self, num):
        cleanNum = ""
        for i in range(len(num)):
            if num[i] == '.' and i != len(num) - 3:
                continue
            elif num[i] == ',':
                continue
            cleanNum += num[i]
        return cleanNum

    def get_date_and_id_from_title(self, title):
        re1 = title.split("@")
        photo_id = re1[0].split("_")[1]
        date = re1[1].split("_")[0]
        return photo_id, date

    def transfer_amount(self, content):
        # return the amounts present in the content
        result = set()
        # find with digit and decimal
        for i in re.finditer(r"\d{1,3}(?:,\d{3})*(?:\.\d+)+", content):
            #print(i)
            result.add(i.group())
        #find with S digit and deciaml
        # for i in re.finditer(r"(\b[S][0-9]*\.[0-9]*)|\b[S][0-9]+", content):
        #     print(i.group())
        #     result.add(i.group()[1:])
        for i in re.finditer(r"\b[S]\d{1,3}(?:,\d{3})*(?:\.\d+)+|\b[S]\d{1,3}(?:,\d{3})*", content):
            # print(i.group())
            result.add(i.group()[1:])
        # find with $ digit and decimal
        # for i in re.finditer(r"\$\d+(?:\.\d+)?", content):
        #     print(i.group())
        #     result.add(i.group()[1:])
        for i in re.finditer(r"\$\d{1,3}(?:,\d{3})*(?:\.\d+)+|\$\d{1,3}(?:,\d{3})*", content):
            # print(i.group())
            result.add(i.group()[1:])
        final = set()

        if len(result) > 1:
            for i in result:
                if '.' in i:
                    num = self.clean_number(i)
                    final.add(float(num))  
            if final:
                return [max(final)]
            else:
                return []
        else:
            return result
    

    def money_application(self):
        pass

    def digital_pay(self):
        pass

    def digital_pay_type(self, content):
        """check names before checking most dominant colors
        ie if it says paypal there is no need to check if there is blue. 
        for cashapp, check if there is a username ($CashappName) before 
        checking for the green color"""
        dig_type_list = ["paypal", "cash"]
        re = []
        content_lower = content.lower()
        for i in dig_type_list:
            if i in content_lower:
                re.append(i)
        return re


        pass

    def official_deposit(self):
        pass

    def data_assign_rowby(self, photo_id, date, mt_application, dig_payment, dig_payment_type, amount, official_dep, writer):
        num_amount = len(amount)
        # amount = [float(i) for i in amount]
        amount.sort()
        writer.writerow([photo_id, date, mt_application, dig_payment, dig_payment_type, amount, official_dep])


if __name__ == '__main__':
    folder_textdoc_path = 'C:/Users/jonat/OneDrive/Documents/VisualStudioRepositories/Money_Transfer_Parser/money-tranfer-sample-textfiles'
    textdoc_paths = base_parser.get_textdoc_paths(folder_textdoc_path)
    headerList = ['Pic ID', 'Date', 'Money Transfer Application', 'Digital Payments', 'Digital Payment Type', 'Amount', 'Official Deposit']
    with open('money_transfers_file'+'.csv','w', newline='', encoding='utf-8') as f1:
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
            print(file_name[-34:-4])
            #### parse photo id and date
            photo_id, date = transfer.get_date_and_id_from_title(file_name)
            if photo_id:
                transfer.photo_id = photo_id
            if date:
                transfer.date = date

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
            print(digital_pay)
            if digital_pay:
                if digital_pay[0] == "cash":
                    transfer.dig_payment_type = "CashApp"
                else:
                    transfer.dig_payment_type = digital_pay[0]
                transfer.dig_payment = '1'
                
            """else:
                #dig_payment = '0'"""
            #parse zipcode and state
            if content:
                """info_zipcode = transfer.check_zipcode(text_des)
                transfer.zipcode.extend([i[0] for i in info_zipcode])
                transfer.state.extend([i[1] for i in info_zipcode])
                for i in transfer.zipcode:
                    print("zip", i)
                for i in transfer.state:
                    print("state", i)
 
                #### parse bankname
                info_bank = check.check_bankname(text_des)
                check.bankname.extend([i for i in info_bank])
                for i in check.bankname:
                    print("bank:",i)"""
                info_amount = transfer.transfer_amount(text_des)
                transfer.amount.extend(i for i in info_amount)

            # for i,code in enumerate(check.zipcode):
            #     writer.writerow()

            #print(check.photo_id, check.date, check.bankname, check.zipcode, check.state, check.amount)
            # writer.writerow([check.photo_id, check.date, check.bankname, check.zipcode, check.state, check.amount])
            transfer.data_assign_rowby(transfer.photo_id, transfer.date, transfer.mt_application, transfer.dig_payment, transfer.dig_payment_type, transfer.amount, transfer.official_dep, writer)

        # exit()
        