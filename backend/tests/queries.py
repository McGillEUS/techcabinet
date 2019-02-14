query_items = '''
{
  allItems{
    edges{
      node{
        id,
        name,
        dateIn,
        dateOut,
        quantity
      }
    }
  }
}
'''

create_item = '''
mutation{
  createItem(itemName:"%s", quantity: %i, username: "%s", authToken: "%s"){
    items{
      id,
      name,
      dateIn,
      dateOut,
      quantity
    }
  }
}'''

create_user = '''
mutation{
  registerUser(username:"%s", password:"%s", email:"%s", studentId:"%s", admin:%s, supersecretpassword:"%s"){
    authToken
  }
}
'''

delete_item = '''
mutation{
  deleteItem(itemName:"%s", username:"%s", authToken:"%s"){
    items{
      id,
      name,
      dateIn,
      dateOut,
      quantity
    }
  }
}
'''

log_in = '''
mutation{
  loginUser(username:"%s", password:"%s"){
    authToken
  }
}
'''

validate_token = '''
mutation{
  validateToken(username:"%s", authToken:"%s"){
    valid
  }
}
'''
