const tableStyles = theme => ({
    root: {
      width: '100%',
      marginTop: theme.spacing.unit * 3,
      overflowX: 'auto',
    },
    table: {
      minWidth: 700,
    },
  });
  
const textBoxStyles = theme => ({
    textField: {
      marginLeft: theme.spacing.unit,
      marginRight: theme.spacing.unit,
    },
    
    button: {
      marginTop: 16,
    },
    
    dense: {
      marginTop: 16,
    },
    menu: {
      width: 200,
    },
  });

  export { tableStyles, textBoxStyles }