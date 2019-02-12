import React, { Component } from 'react';
import axios from 'axios';
import logo from './logo.svg';
import PropTypes from 'prop-types';

import Button from '@material-ui/core/Button';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import { withStyles } from '@material-ui/core/styles';

import { SimpleTable, SimpleTextField } from './components'
import { tableStyles, textBoxStyles } from './styles'
import { GET_ITEMS } from './requests'

import './App.css';

const axiosGraphQL = axios.create({
  baseURL: 'http://127.0.0.1:5000/graphql',
  headers: {}
});

SimpleTextField.propTypes = {
  classes: PropTypes.object.isRequired,
};

SimpleTable.propTypes = {
  classes: PropTypes.object.isRequired
};

const RentalTable = withStyles(tableStyles)(SimpleTable);
const SimpleStyledTextField = withStyles(textBoxStyles)(SimpleTextField);

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      results: [],
      transactions: [],
      tokenValidity: 0,
      authToken: "",
      username: "",
      loading: true
    };
    this.checkOutItem = this.checkOutItem.bind(this);
    this.checkInItem = this.checkInItem.bind(this);
    this.createItem = this.createItem.bind(this);
    this.deleteItem = this.deleteItem.bind(this);
    this.requestItem = this.requestItem.bind(this);
    this.acceptOrder = this.acceptOrder.bind(this);
    this.logIn = this.logIn.bind(this);
  }

  componentDidMount() {
    this.getAllItems();
    this.verifyAuthentication();
  }

  getAllItems() {
    axiosGraphQL
      .post('', { query: GET_ITEMS })
      .then(results => {this.setState({results: results.data.data.showItems.items})},
            error => {console.log(error)});
  };

  getAllTransactions(){
    let GET_TRANSACTIONS = `
    mutation{
    showTransactions(username: "${this.state.username}", authToken: "${this.state.authToken}"){
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
    axiosGraphQL
    .post('', { query: GET_TRANSACTIONS })
    .then(results => {this.setState({transactions: results.data.data.showTransactions.transactions})},
          error => {console.log(error)});
  }

  
  checkOutItem(name, quantity, checkedOutBy) {
    let CHECKOUT_ITEM = `
    mutation{
      checkOutItem(name: "${name}", quantity: ${quantity}, checkedOutBy: "${checkedOutBy}"){
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
          quantity
        }
      }
    }
  `;
    axiosGraphQL
      .post('', { query: CHECKIN_ITEM} )
      .then(results => {this.setState({results: results.data.data.checkInItem.items})},
            error => {console.log(error); console.log(CHECKIN_ITEM)});
  }

  createItem(itemName, quantity){
    let CREATE_ITEM = `
    mutation{
      createItem(authToken: "${this.state.authToken}", username: "${this.state.username}", itemName: "${itemName}", quantity: ${quantity}){
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

  deleteItem(name){
    let DELETE_ITEM = `
      mutation{
        deleteItem(name: "${name}"){
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
    axiosGraphQL
    .post('', { query: DELETE_ITEM })
    .then(results => {this.setState({results: results.data.data.deleteItem.items})},
          error => {console.log(error)});
  }

  requestItem(itemName, userName, email, studentId, quantity){
    let REQUEST_ITEM = `
      mutation{
        checkOutItem(name: "${itemName}", email: "${email}", studentId: "${studentId}", requestedBy: "${userName}", quantity: ${quantity}){
          items{
            id,
            name,
            dateIn,
            dateOut,
            quantity
          }
        }
      }
    `
    axiosGraphQL
    .post('', { query: REQUEST_ITEM })
    .then(results => {this.setState({results: results.data.data.checkOutItem.items})},
          error => {console.log(error)});
  }

  acceptOrder(userRequestedId, itemName){
    let ACCEPT_ORDER = `
      mutation{
        acceptCheckoutRequest(userRequestedId: ${userRequestedId}, userAcceptedName: "${this.state.username}", userAcceptedEmail:"Chris@mail", itemId:${itemName}){
          transactions{
            id,
            dateRequested,
            userRequestedId,
            userAccepted,
            accepted,
            itemId
          }
        }
      }
    `
    axiosGraphQL
    .post('', { query: ACCEPT_ORDER })
    .then(results => {this.setState({transactions: results.data.data.acceptCheckoutRequest.transactions})},
          error => {console.log(error)});
  }

  verifyAuthentication(){
    let authToken = localStorage.getItem("authToken");
    let username = localStorage.getItem("username");

    let VALIDATE_TOKEN = `
    mutation{
      validateToken(username: "${username}", authToken:"${authToken}"){
        valid
      }
    }
    `
    axiosGraphQL
    .post('', { query: VALIDATE_TOKEN })
    .then(result => {this.updateAuthenticatedState(authToken, username, result.data.data.validateToken.valid)},
          error => {console.log(VALIDATE_TOKEN); console.log(error); this.setState({loading: false});});
  }

  updateAuthenticatedState(authToken, username, validity_level){
    /* The local state should only contain valid tokens.
     * Tokens have three levels of validity:
     * Level 0: Unauthenticated user
     * Level 1: Authenticated user
     * Level 2: Authenticated administrator
     */
    if (validity_level > 0){
      this.setState({authToken: authToken, username: username, tokenValidity: validity_level});
      this.getAllTransactions();
    }
    this.setState({loading: false});
  }

  logIn(username, password){
    let LOGIN = `
    mutation{
      loginUser(username:"${username}", password:"${password}"){
        authToken
      }
    }
    `
    axiosGraphQL
    .post('', { query: LOGIN })
    .then(results => {this.handleLogInInfo(results, username)},
          error => {console.log(LOGIN); console.log(error)});
  }

  logOut(){
    let LOGOUT = `
    mutation{
      logoutUser(authToken:"${this.state.authToken}"){
        status
      }
    }
    `
    axiosGraphQL
    .post('', { query: LOGOUT })
    .then(result => {result.data.data.logoutUser.status === "success" ? this.setState({tokenValidity: 0}) : console.log("Failed to log out...");
                     window.location.reload();},
          error => {console.log(LOGOUT); console.log(error)});
  }

  handleLogInInfo(results, username){
    if (results.data.data.loginUser != null){
      localStorage.setItem("authToken", results.data.data.loginUser.authToken);
      localStorage.setItem("username", username);
      window.location.reload();
    } else {
      console.log("error");
      console.log(results);
    }
  }

  render() {
    if(this.state.loading){
      return "Loading...";
    }
    return (
      <div className="App">
        <header className="App-header">
            <div className="logo">
              <img src={logo} className="App-logo" alt="logo" />
              <p>Tech Cabinet Rental Platform</p>
            </div>
            <div className="login" style={{display: this.state.tokenValidity > 0 ? "none" : "block" }}>
              <SimpleStyledTextField textFieldLabel1="username" textFieldLabel2="password" label="Log In" type="password" onClickEvent={this.logIn}/>
            </div>
            <div className="welcome" style={{display: this.state.tokenValidity > 0 ? "block" : "none" }}>
            <p> Welcome, {this.state.username}! </p>
            <Button variant="contained" onClick={(e) => this.logOut()}>
              Log Out
            </Button>
            </div>
        </header>
        <div className="container">
          <h1>Available Items</h1>
          <RentalTable tokenValidity={this.state.tokenValidity} results={this.state.results} deleteItem={this.deleteItem} requestItem={this.requestItem}/>
          <div className="form" style={{display: this.state.tokenValidity > 1 ? "block" : "none" }}>
            <SimpleStyledTextField textFieldLabel1="item" textFieldLabel2="quantity" label="Add item" onClickEvent={this.createItem}/>
          </div>
          <br></br>
          <div className="transactions" style={{display: this.state.tokenValidity > 0 ? "block" : "none" }}>
          <h1 style={{display: this.state.tokenValidity === 1 ? "block" : "none" }}> Your Requests </h1>
          <h1 style={{display: this.state.tokenValidity === 2 ? "block" : "none" }}> Request History </h1>
          <Table>
          <TableHead>
            <TableRow>
              <TableCell align="true">User Requesting Item</TableCell>
              <TableCell align="true">Item Requested</TableCell>
              <TableCell align="true">Date Requested</TableCell>
              <TableCell align="true">Quantity Requested</TableCell>
              <TableCell align="true">Order Accepted?</TableCell>
              <TableCell align="true">User Who Accepted The Order</TableCell>
              <TableCell align="true">Date Accepted</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {this.state.transactions.map((row, index) => {
              return (
                <TableRow key={index} onClick={() => this.acceptOrder(row.userRequestedId, row.itemId)}>
                  <TableCell align="true">{row.userRequestedId}</TableCell>
                  <TableCell align="true">{row.itemId}</TableCell>
                  <TableCell align="true">{row.dateRequested}</TableCell>
                  <TableCell align="true">{row.requestedQuantity}</TableCell>
                  <TableCell align="true">{row.accepted ? "Yes" : "No"}</TableCell>
                  <TableCell align="true">{row.userAccepted}</TableCell>
                  <TableCell align="true">{row.dateAccepted}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
          </Table>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
