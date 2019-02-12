# Tech Cabinet

Rental system for the EUS' tech cabinet.

Currently a work-in-progress. The features are slowly being implemented, so code quality is not good (for now).

To run the front-end, navigate to `frontend/` and run:

- `yarn install`
- `yarn start`

To run the back-end, navigate to `backend/` and run:

- `python -m venv venv`
- `source venv/bin/activate`
- `python setup.py`
- `python app.py`

# Text Dump
This will be better documented later, for now it simply outlines the operations users can make on the back-end:

LOGIN:
```
mutation{
  loginUser(username:"potato", password: "potato"){
    authToken
  }
}
```

LOGOUT:
```
mutation{
  logoutUser(authToken: "potato"){
    status
  }
}
```

CHANGE PASSWORD:
```
mutation{
  changePassword(username:"potato", password: "potato2", authToken: "potato"){
    authToken
  }
}
```

VALIDATE:
```
mutation{
  validateToken(username:"potato", authToken: "potato"){
    valid
  }
}
```

SHOW ITEMS:
```
mutation{
  showItems{
    items{
      id,
      name
    }
  }
}
```

SHOW TRANSACTIONS:
```
mutation{
  showTransactions(username:"admin", authToken: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NDk5Nzk3OTYsImlhdCI6MTU0OTk3OTYxNiwiaWQiOjR9.TYWX4pApYGolbC1sY-jbXlKIHNKxtDMlrJV6WDOjO7k"){
    transactions{
      id,
      userRequestedId,
      userAccepted
    }
  }
}
```

REGISTER USERS:
```
mutation{
  registerUser(username:"admin", email:"bob", password:"secret", studentId:"123", supersecretpassword:"foobar", admin: true){
    authToken
  }
}
```


CHECKOUT ITEM:
```
mutation{
  checkOutItem(requestedBy: "potato", quantity: 1, authToken: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NDk5NzkzNTEsImlhdCI6MTU0OTk3OTE3MSwiaWQiOjR9.n443x7B5EVg5F7eqoSVZ-d9OFOcTUr6N7DtBm0EaooM", itemName:"Potato", email:"", password:"", studentId:""){
    items{
      id,
      name
    }
  }
}
```

ACCEPT CHECKOUT REQUEST:
```
mutation{
  acceptCheckoutRequest(userAcceptedName:"admin", authToken: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NDk5Nzk3OTYsImlhdCI6MTU0OTk3OTYxNiwiaWQiOjR9.TYWX4pApYGolbC1sY-jbXlKIHNKxtDMlrJV6WDOjO7k", itemId: 1, userRequestedId: 3){
    transactions{
      id,
      userAccepted,
      dateAccepted
    }
  }
}
```

CHECK IN ITEMS:
```
mutation{
  checkInItem(adminName:"admin", authToken: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NDk5ODAxMTQsImlhdCI6MTU0OTk3OTkzNCwiaWQiOjR9.COCkps2VbX-0-k5cZLx7VzJIilmeFyp8PBkdl7qjU3U", itemId: 1, quantity: 1){
    items{
      id,
      name,
      quantity
    }
  }
}
```
