const GET_ITEMS = `
  mutation{
    showItems{
      items{
        id,
        name,
        dateIn,
        dateOut,
        quantity
      }
    }
  }
`;

const GET_TRANSACTIONS = `
  mutation{
    showTransactions{
      transactions{
        id,
        accepted,
        userAccepted,
        userRequestedId,
        requestedQuantity,
        dateAccepted,
        dateRequested,
        itemId
      }
    }
  }
`;

export { GET_ITEMS, GET_TRANSACTIONS }