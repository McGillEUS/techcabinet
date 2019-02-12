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


export { GET_ITEMS }