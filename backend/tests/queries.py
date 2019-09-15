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
  createItem(itemName:"%s", quantity: %i, email: "%s", authToken: "token"){
    items{
      id,
      name,
      dateIn,
      dateOut,
      quantity
    }
  }
}'''

create_admin = '''
mutation{
  createAdmin(email: "%s", name: "%s", password:"%s"){
    admins{
      email
    }
  }
}
'''

delete_item = '''
mutation{
  deleteItem(itemName:"%s", email:"%s", authToken:"token"){
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

reserve_item = '''
mutation{
  reserveItem(email: "%s", studentId:"%s", itemName:"%s", quantity:%s, authToken: "token"){
    items{
      id,
      name
    }
  }
}
'''

checkout_item = '''
mutation{
  checkOutItem(transactionId: "%s", adminEmail:"%s", item:"%s", authToken: ""){
    transactions{
      id,
      userRequestedId,
      adminAccepted,
      returned
    }
  }
}
'''

checkin_item = '''
mutation{
  checkInItem(adminEmail:"%s", authToken: "", transactionId: "%s", item: "%s"){
    transactions{
      id,
      userRequestedId,
      adminAccepted,
      returned
    }
  }
}
'''

show_transactions = '''
mutation{
  showTransactions(email:"%s", authToken: ""){
    transactions{
      id,
      userRequestedId,
      adminAccepted
    }
  }
}
'''
