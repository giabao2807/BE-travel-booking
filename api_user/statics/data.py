from enum import Enum


class RoleData(Enum):
    ADMIN = {
        "id": "7a8f585dccb049ada11653bd0f550d59",
        "name": "Admin",
        "description": "administrator",
    }

    CUSTOMER = {
        "id": "45905ee5131544cf8f8235cb9d838b75",
        "name": "Customer",
        "description": "Customer of Travel",
    }

    PARTNER = {
        "id": "246c670ed51b4d7daa5f77d42f68a91d",
        "name": "Partner",
        "description": "Partner",
    }


ProfileData = {
    "customer_account": [
        {
            "email": "binhnguyen148@gmail.com",
            "avatar": "https://res.cloudinary.com/boninguci/image/upload/v1681402720/DATN/avatar/Ag%CC%86layan_kedy_oqxwsm.jpg",
            "last_name": "Nguyen My",
            "first_name": "Binh",
            "gender": 2,
            "birthday": "1976-08-14",
            "address": "Quang Nam",
            "phone": "0904270001",
        },
        {
            "email": "thuongnd5@fsoft.com.vn",
            "avatar": "https://res.cloudinary.com/boninguci/image/upload/v1681402715/DATN/avatar/%D0%9A%D0%BE%D1%82%D0%B8%D0%BA_ijoazd.jpg",
            "last_name": "Nguyen Duy",
            "first_name": "Thuong",
            "gender": 1,
            "birthday": "2000-11-01",
            "address": "Quang Nam",
            "phone": "0122345578",
        },
        {
            "email": "huyle@paradox.com",
            "avatar": "https://res.cloudinary.com/boninguci/image/upload/v1681402720/DATN/avatar/Ag%CC%86layan_kedy_oqxwsm.jpg",
            "last_name": "Le Cao Viet",
            "first_name": "Huy",
            "gender": 1,
            "birthday": "2000-08-25",
            "address": "Quang Nam",
            "phone": "0909079677",
        },
        {
            "email": "ngandtt9@fsoft1.com",
            "avatar": "https://res.cloudinary.com/boninguci/image/upload/v1681402720/DATN/avatar/Ag%CC%86layan_kedy_oqxwsm.jpg",
            "last_name": "Doan",
            "first_name": "Ngan",
            "gender": 2,
            "birthday": "1995-08-18",
            "address": "Quang Nam",
            "phone": "0909152819",
        },
        {
            "email": "huydq53@fsoft.com",
            "avatar": "https://res.cloudinary.com/boninguci/image/upload/v1681402720/DATN/avatar/Ag%CC%86layan_kedy_oqxwsm.jpg",
            "last_name": "Do Quang",
            "first_name": "Huy",
            "gender": 1,
            "birthday": "2000-08-18",
            "address": "Phu Yen",
            "phone": "0909152819",
        },
    ],
    "partner_account": [
        {
            "email": "nguyenduythuong2k@gmail.com",
            "avatar": "https://res.cloudinary.com/boninguci/image/upload/v1681402715/DATN/avatar/%D0%9A%D0%BE%D1%82%D0%B8%D0%BA_ijoazd.jpg",
            "last_name": "Nguyen Duy",
            "first_name": "Thuong",
            "gender": 1,
            "birthday": "2000-11-01",
            "address": "Quang Nam",
            "phone": "0909079677",
        },
        {
            "email": "nhannth5@fsoft1.com.vn",
            "avatar": "https://res.cloudinary.com/boninguci/image/upload/v1681402720/DATN/avatar/Ag%CC%86layan_kedy_oqxwsm.jpg",
            "last_name": "Nguyen",
            "first_name": "Nhan",
            "gender": 2,
            "birthday": "2002-08-25",
            "address": "Hue",
            "phone": "0909079677",
        }
    ],
    "admin_account": [
        {
            "email": "dinhgiabao2807@gmail.com",
            "avatar": "https://res.cloudinary.com/boninguci/image/upload/v1681402702/DATN/avatar/Save_Follow_udyxtx.jpg",
            "last_name": "Dinh Gia",
            "first_name": "Bao",
            "gender": 2,
            "birthday": "2001-08-27",
            "address": "Quang Nam",
            "phone": "0915181914",
        }
    ]
}
