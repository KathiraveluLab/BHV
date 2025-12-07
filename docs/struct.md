```
bhv/
├── bhv/
│   ├── main.py               
│   ├── cli.py                
│   │
│   ├── core/
│   │   ├── config.py         
│   │   ├── security.py       
│   │   ├── db.py             
│   │   └── roles.py          
│   │
│   ├── auth/
│   │   ├── routes.py         
│   │   ├── models.py
│   │
│   ├── users/
│   │   ├── routes.py
│   │   └── models.py
│   │
│   ├── images/
│   │   ├── routes.py         
│   │   ├── models.py
│   │   └── services.py       
│   │
│   ├── storage/
│   │   ├── local.py          
│   │   └── github.py         
│   │
│   ├── admin/
│   │   ├── routes.py         
│   │   └── dashboard.py
│   │
│   ├── ui/
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── upload.html
│   │   └── admin.html
│   │
│   ├── static/
│   │   └── uploads/          
│   │
│   └── audit/
│       └── logger.py    
│   
│     
│
├── tests/
├── Dockerfile
├── pyproject.toml
├── README.md               
└── .env.example
