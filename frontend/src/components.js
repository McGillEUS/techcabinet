import React, { Component } from 'react';
import TextField from '@material-ui/core/TextField';
import Paper from '@material-ui/core/Paper';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import Button from '@material-ui/core/Button';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';


class LoggedOutDialog extends React.Component{
  render(){
    return(
      <DialogContent>
        <DialogContentText>
          You are checking out: "<b>{this.props.item}</b>".<br></br>
          Please fill the information below to create an account.<br></br>
          If you have already created an account, please log in.<br></br>
          Once your request is submitted, you can log in to track your requests.<br></br>
          If you have any issues, please contact <b>it.director@mcgilleus.ca</b> for support.
        </DialogContentText>
        <TextField
          autoFocus
          margin="dense"
          id="email"
          label="Email Address"
          type="email"
          helperText={this.props.errors['email']}
          error={this.props.errors['email'].length > 0}
          fullWidth
          onChange={this.props.handleChange('email')}
        />
        <TextField
          autoFocus
          margin="dense"
          id="name"
          label="Username"
          type="name"
          helperText={this.props.errors['username']}
          error={this.props.errors['username'].length > 0}
          fullWidth
          onChange={this.props.handleChange('name')}
        />
        <TextField
          autoFocus
          margin="dense"
          id="password"
          label="Password"
          type="password"
          helperText={this.props.errors['password']}
          error={this.props.errors['password'].length > 0}
          fullWidth
          onChange={this.props.handleChange('password')}
        />
        <TextField
          autoFocus
          margin="dense"
          id="id"
          label="Student ID"
          type="id"
          helperText={this.props.errors['student_id']}
          error={this.props.errors['student_id'].length > 0}
          fullWidth
          onChange={this.props.handleChange('studentid')}
        />
        <TextField
          autoFocus
          margin="dense"
          id="id"
          label="Quantity"
          type="id"
          helperText={this.props.errors['quantity']}
          error={this.props.errors['quantity'].length > 0}
          fullWidth
          onChange={this.props.handleChange('quantity')}
        />
      </DialogContent>
    )
  }
}

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
          error={this.props.errors['quantity'].length === 0}
          label="Quantity"
          type="id"
          fullWidth
          onChange={this.props.handleChange('quantity')}
        />
      </DialogContent>
    )
  }
}


class RequestDialog extends React.Component{
    state = {
      name: '',
      email: '',
      password: '',
      studentid: '',
      quantity: ''
    };

    handleChange = name => event => {
      this.setState({
        [name]: event.target.value,
      });
    };

    dialog = (item) => this.props.tokenValidity > 0 ? <LoggedInDialog item={item} errors={this.props.errors} handleChange={this.handleChange}/>
                                                    : <LoggedOutDialog item={item} errors={this.props.errors} handleChange={this.handleChange}/>;
    deleteButton = this.props.tokenValidity > 1 ? <Button onClick={this.props.deleteDialogAction} color="primary"> Delete </Button>
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
          <Button onClick={() => {this.props.submitDialogAction(this.state.quantity, this.state.name,
                                                                this.state.password, this.state.email,
                                                                this.state.studentid);}}
                  color="primary">
            Submit
          </Button>
          {this.deleteButton}
        </DialogActions>
      </Dialog>
      )
    }
}

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
      this.submitDialog = this.submitDialog.bind(this);
      this.deleteDialog = this.deleteDialog.bind(this);
    }

    handleClick(name){
      this.setState({dialogVisible: true, item: name});
    }

    closeDialog(){
      this.setState({dialogVisible: false});
    }
    
    validateEmail(email) {
      // Credit: https://stackoverflow.com/questions/46155/how-to-validate-an-email-address-in-javascript
      var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(String(email).toLowerCase());
    }

    submitDialog(quantity, username, password, email, studentID){
      let validInput = true;
      let errors = this.state.errors
      errors['quantity'] = "";
      if (quantity <= 0){
        errors['quantity'] = "Quantity must be greater than zero.";
        validInput = false;
      }
      if (this.props.tokenValidity > 0 && validInput){
          this.props.requestItem(this.state.item, quantity);
      } else {
        errors['username'] = "";
        if (!username || username.length <= 0 || username.length > 100){
          errors['username'] = "You must input a username between 0 and 100 characters.";
          validInput = false;
        }
        errors['password'] = "";
        if(!password){
          errors['password'] = "You must input a password.";
          validInput = false;
        }
        errors['email'] = "";
        if(!email || !this.validateEmail(email)){
          errors['email'] = "You have inputted an invalid email.";
          validInput = false;
        }
        errors['student_id'] = "";
        if(!studentID || studentID.length <= 5 || isNaN(studentID)){
          errors['student_id'] = "Your student ID should be a 6-7 digit number.";
          validInput = false;
        }
        this.setState({errors: errors});
        if (validInput){
          this.props.requestItem(this.state.item, quantity, username,
            password, email, studentID);
        }
      }
      if (validInput){
        this.setState({dialogVisible: false});
      }
    }

    deleteDialog(){
      this.props.deleteItem(this.state.item);
      this.setState({dialogVisible: false});
    }

    render(){
      return (
        <Paper className={this.props.classes.root}>
          <RequestDialog tokenValidity={this.props.tokenValidity} visible={this.state.dialogVisible} item={this.state.item}
                         closeDialogAction={this.closeDialog} submitDialogAction={this.submitDialog} deleteDialogAction={this.deleteDialog}
                         errors={this.state.errors}/>
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

export { SimpleTable, SimpleTextField }