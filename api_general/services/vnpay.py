import hashlib
import hmac
import urllib.parse

import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()


class VNPayPayload:

    def __init__(self, amount, client_ip, bank_code, order_id, order_info):
        self.amount = amount
        self.create_date = datetime.now().strftime('%Y%m%d%H%M%S')
        self.return_url = os.getenv("VNPAY_RETURN_URL")
        self.client_ip = client_ip
        self.bank_code = bank_code
        self.order_id = order_id
        self.order_info = order_info
        self.tmn_code = os.getenv("VNPAY_TMN_CODE")

    def to_dict(self):
        return {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": self.amount,
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": self.order_id,
            "vnp_OrderInfo": self.order_info,
            "vnp_OrderType": "billpayment",
            "vnp_Locale": "vn",
            "vnp_BankCode": self.bank_code,
            "vnp_CreateDate": datetime.now().strftime('%Y%m%d%H%M%S'),
            "vnp_IpAddr": self.client_ip,
            "vnp_ReturnUrl": self.return_url,
        }


class VNPayTransaction:
    requestData = {}
    responseData = {}

    def __init__(self, amount, client_ip, bank_code, order_id, order_info):
        self.base_url = os.getenv("VNPAY_BASE_URL")
        self.secret_key = os.getenv("VNPAY_SECRET_KEY")
        self.url = ""
        self.payload = VNPayPayload(amount, client_ip, bank_code, order_id, order_info)

    def build_payment_url(self):
        request_payload = self.payload.to_dict()
        request_data = sorted(request_payload.items())
        query_strings = [
            key + '=' + urllib.parse.quote_plus(str(val))
            for key, val in request_data
        ]
        query_string = "&".join(query_strings)
        hash_value = self.hmacsha512(self.secret_key, query_string)

        self.url = self.base_url + "?" + query_string + '&vnp_SecureHash=' + hash_value

    # def validate_response(self, secret_key):
    #     vnp_SecureHash = self.responseData['vnp_SecureHash']
    #     # Remove hash params
    #     if 'vnp_SecureHash' in self.responseData.keys():
    #         self.responseData.pop('vnp_SecureHash')
    #
    #     if 'vnp_SecureHashType' in self.responseData.keys():
    #         self.responseData.pop('vnp_SecureHashType')
    #
    #     inputData = sorted(self.responseData.items())
    #     hasData = ''
    #     seq = 0
    #     for key, val in inputData:
    #         if str(key).startswith('vnp_'):
    #             if seq == 1:
    #                 hasData = hasData + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
    #             else:
    #                 seq = 1
    #                 hasData = str(key) + '=' + urllib.parse.quote_plus(str(val))
    #     hashValue = self.hmacsha512(secret_key, hasData)
    #
    #     print(
    #         'Validate debug, HashData:' + hasData + "\n HashValue:" + hashValue + "\nInputHash:" + vnp_SecureHash)
    #
    #     return vnp_SecureHash == hashValue

    @staticmethod
    def hmacsha512(key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()

    @classmethod
    def validate_response(cls, query_params: dict) -> bool:
        secret_hash = query_params.pop("vnp_SecureHash")
        query_params = sorted(query_params.items())
        secret_key = os.getenv("VNPAY_SECRET_KEY")
        query_string = "&".join(
            [
                f"{_key}={urllib.parse.quote_plus(_value)}"
                for _key, _value in query_params
            ]
        )
        return cls.hmacsha512(secret_key, query_string) == secret_hash
