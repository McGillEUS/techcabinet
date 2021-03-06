import React from 'react';
import Button from '@material-ui/core/Button';
import clsx from 'clsx';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import ErrorIcon from '@material-ui/icons/Error';
import Paper from '@material-ui/core/Paper';
import SnackbarContent from '@material-ui/core/SnackbarContent';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TextField from '@material-ui/core/TextField';

/**
 * Dialog screen displayed when a user checks out an item and is logged out.
 * The user effectively creates an account after seeing this dialog, so they are
 * asked to enter their personal information.
 */
class LoggedOutDialog extends React.Component{
  render(){
    return(
      <DialogContent>
        <DialogContentText>
          Please log in to create a reservation.<br></br>
          If you have any issues, please contact <b>it.director@mcgilleus.ca</b> for support.
        </DialogContentText>
      </DialogContent>
    )
  }
}

/**
 * Dialog screen displayed when a user checks out an item and is logged in.
 * Given that the user will authenticate the checkout with their current account,
 * this simply asks for the quantity of the item they request.
 */
class LoggedInDialog extends React.Component{
  render(){
    return(
      <DialogContent>
        <DialogContentText>
          You are checking out: "<b>{this.props.item}</b>"
        </DialogContentText>
        <TextField
          autoFocus
          margin="dense"
          id="id"
          helperText={this.props.errors['quantity']}
          error={this.props.errors['quantity'].length > 0}
          label="Quantity"
          type="integer"
          fullWidth
          onChange={this.props.handleChange('quantity')}
        />
        <TextField
          autoFocus
          margin="dense"
          id="id"
          helperText={this.props.errors['student_id']}
          error={this.props.errors['student_id'].length > 0}
          label="Student ID"
          type="id"
          fullWidth
          onChange={this.props.handleChange('studentId')}
        />
      </DialogContent>
    )
  }
}

/**
 * Generic setup for the dialog to request items.
 * This generic component will either contain a LoggedInDialog or LoggedOutDialog.
 */
class RequestDialog extends React.Component{
    state = {
      studentId: '',
      quantity: ''
    };

    handleChange = name => event => {
      this.setState({
        [name]: event.target.value,
      });
    };

    dialog = (item) => this.props.tokenValidity > 0 ? <LoggedInDialog item={item} errors={this.props.errors} handleChange={this.handleChange} />
                                                    : <LoggedOutDialog item={item} />;
    deleteButton = this.props.tokenValidity > 1 ? <Button onClick={this.props.deleteDialogAction} color="primary"> Delete </Button>
                                                : null;
    submitButton = this.props.tokenValidity > 0 ? <Button onClick={() => {this.props.submitDialogAction(this.state.quantity, this.state.studentId);}} color="primary">Submit</Button>
                                            : null;

    render(){
      return(
        <Dialog open={this.props.visible} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">Check Out Form</DialogTitle>
        {this.dialog(this.props.item)}
        <DialogActions>
          <Button onClick={this.props.closeDialogAction} color="primary">
            Cancel
          </Button>
          {this.deleteButton}
          {this.submitButton}
        </DialogActions>
      </Dialog>
      )
    }
}

/**
 * Meant to be a generic table but has been customized to support only displaying items.
 * State elements:
 * `dialogVisible`: Whether the checkout request dialog should be shown to the user or not
 * `item`: Name of the dialog being checked out
 * `errors`: Dict containing errors that may be shown to the user for various request dialog fields.
 */
class SimpleTable extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        dialogVisible: false,
        item: "",
        errors: {'email': '', 'username': '', 'password': '',
        'student_id': '', 'quantity': ''}
      };
      this.closeDialog = this.closeDialog.bind(this);
      this.deleteDialog = this.deleteDialog.bind(this);
      this.submitDialog = this.submitDialog.bind(this);
    }

    /**
     * Handler for clicks on a row from the items table
     * @param {string} name 
     */
    handleClick(name){
      this.setState({dialogVisible: true, item: name});
    }

     /**
     * Handler for clicking "submit" button in the request dialog
     * More information on this function can be found in the function `reserveItem`
     * from `App.js`.
     * @param {int} quantity
     * @param {string} studentId
     */
    submitDialog(quantity, studentId){
      if (!this.state.dialogVisible){
        return;
      }
      // By default, input is valid and the errors match what is currently in the state.
      let validInput = true;
      let errors = this.state.errors

      // We always reset the error to empty by default, then update it if the input is erroneous.
      // First, validate quantity (this is relevant to users logged in and out)
      errors['quantity'] = "";
      errors['student_id'] = "";

      if (quantity <= 0){
        errors['quantity'] = "Quantity must be greater than zero.";
        validInput = false;
      }

      // Verify that a valid student ID has been provided
      errors['student_id'] = "";
      if(!studentId || studentId.length <= 5 || isNaN(studentId)){
        errors['student_id'] = "Your student ID should be a 6 digit number.";
        validInput = false;
      }

      // Update state to display errors and request item if the input is valid.
      this.setState({errors: errors});
      if (validInput){
        this.props.reserveItem(this.state.item, quantity, studentId);
      }

      // Hide the dialog if the item has been successfully requested
      if (validInput){
        this.setState({dialogVisible: false});
      }
    }

    /**
     * Handler for clicking the "close" button in the request dialog
     */
    closeDialog(){
      this.setState({dialogVisible: false});
    }

    // Handler for clicking "delete" button in the request dialog
    deleteDialog(){
      this.props.deleteItem(this.state.item);
      this.setState({dialogVisible: false});
    }

    render(){
      return (
        <Paper className={this.props.classes.root}>
          <RequestDialog tokenValidity={this.props.tokenValidity} visible={this.state.dialogVisible} item={this.state.item}
                         closeDialogAction={this.closeDialog} deleteDialogAction={this.deleteDialog}
                         submitDialogAction={this.submitDialog} errors={this.state.errors}/>
          <Table className={this.props.classes.table}>
            <TableHead>
              <TableRow>
                <TableCell>Tech Item</TableCell>
                <TableCell align="true">Quantity</TableCell>
                <TableCell align="true">Last Check out At...</TableCell>
                <TableCell align="true">Last Check in At...</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {this.props.results.map((row, index) => {
                return (
                  <TableRow onClick={() => this.handleClick(row.name)} key={index}>
                    <TableCell component="th" scope="row">
                      {row.name}
                    </TableCell>
                    <TableCell align="true">{row.quantity}</TableCell>
                    <TableCell align="true">{row.dateOut}</TableCell>
                    <TableCell align="true">{row.dateIn}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Paper>
      );
    }
}

/**
 * Generic text field, that is reused for the item creation form.
 * Simply contains two text fields and a button.
 */
class SimpleTextField extends React.Component {
    state = {
      textFieldLabel1: '',
      textFieldLabel2: ''
    };
  
    handleChange = name => event => {
      this.setState({
        [name]: event.target.value,
      });
    };
  
    render() {
      const { classes } = this.props;
  
      return (
        <form className={classes.container} noValidate autoComplete="off">
          <TextField
            id="field-1"
            label={this.props.textFieldLabel1}
            className={this.props.classes.textField}
            error={this.props.errors != null && this.props.errors.length > 0}
            helperText={this.props.errors}
            onChange={this.handleChange('textFieldLabel1')}
            margin="normal"
            variant="filled"
          />
          <TextField
            id="field-2"
            label={this.props.textFieldLabel2}
            className={this.props.classes.textField}
            error={this.props.errors != null && this.props.errors.length > 0}
            onChange={this.handleChange('textFieldLabel2')}
            margin="normal"
            variant="filled"
            type={this.props.type}
          />
          <Button variant="contained" className={this.props.classes.button} onClick={ (e) => this.props.onClickEvent(this.state.textFieldLabel1, this.state.textFieldLabel2) }>
            {this.props.label}
          </Button>
        </form>
      );
    }
}

class Alerts extends React.Component {
  render() {
    const { className, message, variant } = this.props;
    const Icon = variant === 'success' ? CheckCircleIcon : ErrorIcon;

    return (
      <SnackbarContent
        className={clsx(this.props.classes[variant], className)}
        aria-describedby="client-snackbar"
        message={
          <span id="client-snackbar" className={this.props.classes.message}>
            <Icon className={clsx(this.props.classes.icon, this.props.classes.iconVariant)} />
            {message}
          </span>
        }
      />
    )
  }
}

export { SimpleTable, SimpleTextField, Alerts }
