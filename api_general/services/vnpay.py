# import hashlib
# import hmac
# import urllib.parse
#
# import os
# from datetime import datetime
#
# from dotenv import load_dotenv
# load_dotenv()
#
#
# class VNPayPayload:
#     properties_mapping = {
#         "version"
#     }
#
#     def __init__(self):
#         self.version = "2.1.0"
#         self.command = "pay"
#         self.currency_code = "VND"
#         self.locale = "vn"
#         self.create_date = datetime.now().strftime('%Y%m%d%H%M%S')
#         self.return_url = os.getenv("VNPAY_RETURN_URL")
#         self.client_ip = ?
#
# class VNPayTransaction:
#     requestData = {}
#     responseData = {}
#
#     def __init__(self):
#         base_url = os.getenv("VNPAY_BASE_URL")
#         secret_key = os.getenv("VNPAY_SECRET_KEY")
#         vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
#         vnp.requestData['vnp_Amount'] = amount * 100
#         vnp.requestData['vnp_TxnRef'] = order_id
#         vnp.requestData['vnp_OrderInfo'] = order_desc
#         vnp.requestData['vnp_OrderType'] = order_type
#         # Check language, default: vn
#         if language and language != '':
#             vnp.requestData['vnp_Locale'] = language
#         else:
#             # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
#         if bank_code and bank_code != "":
#             vnp.requestData['vnp_BankCode'] = bank_code
#
#           # 20150410063022
#         vnp.requestData['vnp_IpAddr'] = ipaddr
#         vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
#     def get_payment_url(self, vnpay_payment_url, secret_key):
#         inputData = sorted(self.requestData.items())
#         queryString = ''
#         hasData = ''
#         seq = 0
#         for key, val in inputData:
#             if seq == 1:
#                 queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
#             else:
#                 seq = 1
#                 queryString = key + '=' + urllib.parse.quote_plus(str(val))
#
#         hashValue = self.__hmacsha512(secret_key, queryString)
#         return vnpay_payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue
#
#     def validate_response(self, secret_key):
#         vnp_SecureHash = self.responseData['vnp_SecureHash']
#         # Remove hash params
#         if 'vnp_SecureHash' in self.responseData.keys():
#             self.responseData.pop('vnp_SecureHash')
#
#         if 'vnp_SecureHashType' in self.responseData.keys():
#             self.responseData.pop('vnp_SecureHashType')
#
#         inputData = sorted(self.responseData.items())
#         hasData = ''
#         seq = 0
#         for key, val in inputData:
#             if str(key).startswith('vnp_'):
#                 if seq == 1:
#                     hasData = hasData + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
#                 else:
#                     seq = 1
#                     hasData = str(key) + '=' + urllib.parse.quote_plus(str(val))
#         hashValue = self.__hmacsha512(secret_key, hasData)
#
#         print(
#             'Validate debug, HashData:' + hasData + "\n HashValue:" + hashValue + "\nInputHash:" + vnp_SecureHash)
#
#         return vnp_SecureHash == hashValue
#
#     @staticmethod
#     def __hmacsha512(key, data):
#         byteKey = key.encode('utf-8')
#         byteData = data.encode('utf-8')
#         return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()
