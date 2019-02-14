const GET_ITEMS = `
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
`;


export { GET_ITEMS }