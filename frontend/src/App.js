import React, { Component } from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TextField from '@material-ui/core/TextField';
import Paper from '@material-ui/core/Paper';
import logo from './logo.svg';
import './App.css';
import { FormHelperText } from '@material-ui/core';

// TODO: Move all these styles elsewhere!!!
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
    display: 'flex',
    marginLeft: '40%',
  },
  
  dense: {
    marginTop: 16,
  },
  menu: {
    width: 200,
  },
});

const axiosGraphQL = axios.create({
  baseURL: 'http://127.0.0.1:5000/graphql',
  headers: {
    
  }
});

// TODO: This one should be maybe in a separate file ...?
class SimpleTable extends React.Component {
  render(){
    return (
      <Paper className={this.props.classes.root}>
        <Table className={this.props.classes.table}>
          <TableHead>
            <TableRow>
              <TableCell>Tech Item</TableCell>
              <TableCell align="true">Quantity</TableCell>
              <TableCell align="true">Last Check out At...</TableCell>
              <TableCell align="true">Last Check in At...</TableCell>
              <TableCell align="true">Checked Out By</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {this.props.results.map((row, index) => {
              return (
                <TableRow key={index}>
                  <TableCell component="th" scope="row">
                    {row.name}
                  </TableCell>
                  <TableCell align="true">{row.quantity}</TableCell>
                  <TableCell align="true">{row.dateOut}</TableCell>
                  <TableCell align="true">{row.dateIn}</TableCell>
                  <TableCell align="true">{row.userOut}</TableCell>
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
        />
        <Button variant="contained" className={this.props.classes.button} onClick={(e) => this.props.onClickEvent(this.state.textFieldLabel1, this.state.textFieldLabel2)}>
          {this.props.label}
        </Button>
      </form>
    );
  }
}


SimpleTextField.propTypes = {
  classes: PropTypes.object.isRequired,
};

SimpleTable.propTypes = {
  classes: PropTypes.object.isRequired
};

const RentalTable = withStyles(tableStyles)(SimpleTable);
const SimpleStyledTextField = withStyles(textBoxStyles)(SimpleTextField);

const GET_ITEMS = `
  mutation{
    showItems{
      items{
        id,
        name,
        dateIn,
        dateOut,
        userOut,
        quantity
      }
    }
  }
`;

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      results: []
    };
    this.checkOutItem = this.checkOutItem.bind(this);
    this.checkInItem = this.checkInItem.bind(this);
    this.createItem = this.createItem.bind(this);
  }

  componentDidMount() {
    this.getAllItems();
  }

  //TODO: `GET` should be handled by `Query` not `Mutation`...
  getAllItems() {
    axiosGraphQL
      .post('', { query: GET_ITEMS })
      .then(results => {this.setState({results: results.data.data.showItems.items})},
            error => {console.log(error)});
  };

  //TODO: checkIn/Out has been tested using hard-coded data;
  //Implement functionality to get data from within table.
  checkOutItem(name, quantity, checkedOutBy) {
    let CHECKOUT_ITEM = `
    mutation{
      checkOutItem(name: "${name}", quantity: ${quantity}, checkedOutBy: "${checkedOutBy}"){
        items{
          id,
          name,
          dateIn,
          dateOut,
          quantity,
          userOut
        }
      }
    }
  `;
    axiosGraphQL
      .post('', { query: CHECKOUT_ITEM} )
      .then(results => {this.setState({results: results.data.data.checkOutItem.items})},
            error => {console.log(error); console.log(CHECKOUT_ITEM)});
  }

  checkInItem(name, quantity) {
    let CHECKIN_ITEM = `
    mutation{
      checkInItem(name: "${name}", quantity: ${quantity}){
        items{
          id,
          name,
          dateIn,
          dateOut,
          quantity,
          userOut
        }
      }
    }
  `;
    axiosGraphQL
      .post('', { query: CHECKIN_ITEM} )
      .then(results => {this.setState({results: results.data.data.checkInItem.items})},
            error => {console.log(error); console.log(CHECKIN_ITEM)});
  }

  createItem(name, quantity){
    console.log(name);
    console.log(quantity);
    let CREATE_ITEM = `
    mutation{
      createItem(name: "${name}", quantity: ${quantity}){
        items{
          id,
          name,
          dateIn,
          quantity
        }
      }
    }
  `;
    axiosGraphQL
    .post('', { query: CREATE_ITEM} )
    .then(results => {console.log(results); this.setState({results: results.data.data.createItem.items})},
          error => {console.log(error); console.log(CREATE_ITEM)});
  }

  deleteItem(){
    console.log("Implement me!");
  }

  logIn(){
    console.log("Implement me!");
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
            <div className="logo">
              <img src={logo} className="App-logo" alt="logo" />
              <p>Tech Cabinet Rental Platform</p>
            </div>
            <div className="login">
              <SimpleStyledTextField textFieldLabel1="username" textFieldLabel2="password" label="Log In" onClickEvent={this.logIn}/>
            </div>
        </header>
        <div className="container">
          <h1>Available Items</h1>
          <RentalTable results={this.state.results}/>
          <div className="form">
            <SimpleStyledTextField textFieldLabel1="item" textFieldLabel2="quantity" label="Add item" onClickEvent={this.createItem}/>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
