const tableStyles = theme => ({
  root: {
    width: '100%',
    marginTop: theme.spacing(3),
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
    backgroundColor: '#eff0ef',
    marginTop: 16,
  },
    
  dense: {
    marginTop: 16,
  },
  menu: {
    width: 200,
  },
});

const alertStyles = theme => ({
  success: {
    backgroundColor: '#43a047',
  },
  error: {
    backgroundColor: theme.palette.error.dark,
  },
  icon: {
    fontSize: 20,
  },
  iconVariant: {
    opacity: 0.9,
    marginRight: theme.spacing(1),
  },
  message: {
    display: 'flex',
    alignItems: 'center',
  },
});

export { tableStyles, textBoxStyles, alertStyles }
