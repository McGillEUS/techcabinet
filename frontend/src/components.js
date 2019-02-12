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

class RequestDialog extends React.Component{
    state = {
      name: '',
      email: '',
      studentid: '',
      quantity: ''
    };

    handleChange = name => event => {
      this.setState({
        [name]: event.target.value,
      });
    };

    render(){
      return(
        <Dialog open={this.props.visible} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">Check out</DialogTitle>
        <DialogContent>
          <DialogContentText>
            You are checking out: "{this.props.item}"
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="email"
            label="Email Address"
            type="email"
            fullWidth
            onChange={this.handleChange('email')}
          />
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Full Name"
            type="name"
            fullWidth
            onChange={this.handleChange('name')}
          />
          <TextField
            autoFocus
            margin="dense"
            id="id"
            label="Student ID"
            type="id"
            fullWidth
            onChange={this.handleChange('studentid')}
          />
          <TextField
            autoFocus
            margin="dense"
            id="id"
            label="Quantity"
            type="id"
            fullWidth
            onChange={this.handleChange('quantity')}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={this.props.closeDialogAction} color="primary">
            Cancel
          </Button>
          <Button onClick={() => {this.props.submitDialogAction(this.state.name,this.state.email,this.state.studentid, this.state.quantity); this.setState({name: '', email: '', studentid: ''})}} color="primary">
            Submit
          </Button>
          <Button onClick={this.props.deleteDialogAction} color="primary">
            Delete
          </Button>
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
        item: ""
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

    submitDialog(user, email, studentID, quantity){
      this.props.requestItem(this.state.item, user, email, studentID, quantity)
      this.setState({dialogVisible: false});
    }

    deleteDialog(){
      this.props.deleteItem(this.state.item);
      this.setState({dialogVisible: false});
    }

    render(){
      return (
        <Paper className={this.props.classes.root}>
          <RequestDialog visible={this.state.dialogVisible} item={this.state.item} closeDialogAction={this.closeDialog} submitDialogAction={this.submitDialog} deleteDialogAction={this.deleteDialog}/>
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
            value={this.state.username}
            onChange={this.handleChange('textFieldLabel1')}
            margin="normal"
            variant="filled"
          />
          <TextField
            id="field-2"
            label={this.props.textFieldLabel2}
            className={this.props.classes.textField}
            value={this.state.password}
            onChange={this.handleChange('textFieldLabel2')}
            margin="normal"
            variant="filled"
            type={this.props.type}
          />
          <Button variant="contained" className={this.props.classes.button} onClick={(e) => this.props.onClickEvent(this.state.textFieldLabel1, this.state.textFieldLabel2)}>
            {this.props.label}
          </Button>
        </form>
      );
    }
}

export { SimpleTable, SimpleTextField }