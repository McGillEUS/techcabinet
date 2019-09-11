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

import { SimpleTable, SimpleTextField, Alerts } from './components'
import { tableStyles, textBoxStyles, alertStyles } from './styles'
import { GET_ITEMS } from './requests'
import { msalInstance } from './msal.js'

import './App.css';

// Deployed URL: 'https://rental.mcgilleus.ca/graphql'
const axiosGraphQL = axios.create({
  baseURL: 'http://127.0.0.1:4293/graphql',
  headers: {}
});

const msalRequestScope = {
  scopes: ["user.read"]
};

// Initialize basic components and specify which part of the front-end they belong to
SimpleTextField.propTypes = {
  classes: PropTypes.object.isRequired,
};

SimpleTable.propTypes = {
  classes: PropTypes.object.isRequired
};

const RentalTable = withStyles(tableStyles)(SimpleTable);
const SimpleStyledTextField = withStyles(textBoxStyles)(SimpleTextField);
const AlertNotifications = withStyles(alertStyles)(Alerts);

// Create main component for the application
class App extends Component {
  /* 
  * State elements of the main application:
  * `results`: The results from querying "items".
  * `transactions`: All transactions a user can see
  * `tokenValidity`: Level of validity of a token (0: invalid, 1: user, 2: admin)
  * `authToken`: Authentication token used for performing back-end queries
  * `username`: Username associated with the token. Mismatching username/token = invalid authentication
  * `authErrors`: Simple string used for showing users authentication errors they might encounter.
  * `errors`: Generic errors from any other action.
  * `loading`: Used to ensure the state is properly loaded before rendering the page so children of `App` can access it.
  */
  constructor(props) {
    super(props);
    this.state = {
      results: [],
      transactions: [],
      tokenValidity: 0,
      authToken: "",
      email: "",
      name: "",
      authErrors: "",
      errors: "",
      loading: true
    };

    // Bind `this` to the various functions which access the state (through `this.state`)
    this.createItem = this.createItem.bind(this);
    this.deleteItem = this.deleteItem.bind(this);
    this.checkOutItem = this.checkOutItem.bind(this);
    this.checkInItem = this.checkInItem.bind(this);
    this.acceptCheckoutRequest = this.acceptCheckoutRequest.bind(this);
    this.logIn = this.logIn.bind(this);
  }

  // Operations to be done after initial render
  componentDidMount() {
    this.getAllItems();
    this.verifyAuthentication();
  }

  /**
   * Basic query, simply retrieves all items for the user.
   */
  getAllItems() {
    axiosGraphQL
      .post('', { query: GET_ITEMS })
      .then(results => {this.setState({results: results.data.data.allItems.edges.map(result => result.node)})},
            error => {console.log(error); console.log(GET_ITEMS)});
  };

  /**
   * Mutation despite also being a `get` because I had trouble implementing the authentication check as a Query.
   * Retrieves all transactions depending on the authentication level of the user (verified on the back-end)
   */
  getAllTransactions(){
    const GET_TRANSACTIONS = `
    mutation{
    showTransactions(email: "${this.state.email}",
                     authToken: "${this.state.authToken}"){
      transactions{
        id,
        accepted,
        returned,
        userAccepted,
        userRequestedId,
        requestedQuantity,
        dateAccepted,
        dateRequested,
        dateReturned,
        item
      }
    }
  }
  `;
  console.log(GET_TRANSACTIONS);
  axiosGraphQL
    .post('', { query: GET_TRANSACTIONS })
    .then(results => {this.setState({transactions: results.data.data.showTransactions.transactions})},
          error => {
            console.log(error);
            this.setState({errors: "Couldn't load all transactions."})
          });
  }

  /**
   * Creates a checkout request for a user.
   * If  the optional fields are not provided, the user must currently be authenticated.
   * @param {string} itemName: Name of the item getting checked out
   * @param {int} quantity: How much of the object is getting checked out
   * @param {string} username: (optional) User requesting to check out the item
   * @param {string} password: (optional) Password of this user
   * @param {string} email: (optional) E-mail of this user
   * @param {string} studentID: (optional) Student ID for this user.
   */
  checkOutItem(itemName, quantity, username, password, email, studentID){
    username = username || this.state.email;
    password = password || "";
    email = email || "";
    studentID = studentID || "";

    const CHECKOUT_ITEM = `
      mutation{
        checkOutItem(requestedBy: "${username}", quantity: ${quantity},
                     authToken: "${this.state.authToken}", itemName:"${itemName}",
                     email:"${email}", password:"${password}", studentId:"${studentID}"){
          items{
            name
          }
        }
      }
    `
    axiosGraphQL
    .post('', { query: CHECKOUT_ITEM })
    .then(
      results => {
        if (results.data.errors.length > 0){
          this.setState({errors: `Checkout request unsuccessful. ${results.data.errors[0].message}`});
        }
        else{
          this.setState({results: results.data.data.checkOutItem.items});
          window.location.reload();
        }
      },
      error => {
        console.log(error);
        console.log(CHECKOUT_ITEM);
        this.setState({errors: `Couldn't check out ${itemName}`});
      });
  }

  /**
   * Administrators accept the check out requests of normal users
   * @param {string} userRequestedId: ID of user who created the checkout request
   * @param {string} transactionId: ID of the transaction being accepted
   * @param {string} item: Name of the item getting checked out
   */
  acceptCheckoutRequest(userRequestedId, transactionId, item) {
    const ACCEPT_CHECKOUT_REQUEST = `
    mutation{
      acceptCheckoutRequest(userRequestedId: "${userRequestedId}", transactionId: "${transactionId}",
                            userAcceptedName: "${this.state.email}", item: "${item}",
                            authToken: "${this.state.authToken}"){
        transactions{
          id,
          accepted,
          returned,
          userAccepted,
          userRequestedId,
          requestedQuantity,
          dateAccepted,
          dateRequested,
          dateReturned,
          item
        }
      }
    }
  `;
    axiosGraphQL
      .post('', { query: ACCEPT_CHECKOUT_REQUEST} )
      .then(results => {
        if (results.data.errors.length > 0){
          this.setState({errors: `Couldn't accept checkout request. ${results.data.errors[0].message}`});
        }
        else{
          this.setState({transactions: results.data.data.acceptCheckoutRequest.transactions});
        }
      },
      error => {
        console.log(error);
        console.log(ACCEPT_CHECKOUT_REQUEST);
        this.setState({errors: `Couldn't accept check out for ${item}`});
      });
  }

  /**
   * Administrators can check items back in.
   * @param {string} item: Name of the item being checked in
   * @param {string} transactionId: ID of the transaction being closed 
   */
  checkInItem(item, transactionId) {
    const CHECKIN_ITEM = `
    mutation{
      checkInItem(item: "${item}", transactionId: "${transactionId}",
                  adminName: "${this.state.email}", authToken: "${this.state.authToken}"){
        transactions{
          id,
          accepted,
          returned,
          userAccepted,
          userRequestedId,
          requestedQuantity,
          dateAccepted,
          dateRequested,
          dateReturned,
          item
        }
      }
    }
  `;
    axiosGraphQL
      .post('', { query: CHECKIN_ITEM} )
      .then(
        results => {
          if (results.data.errors.length > 0){
            this.setState({errors: `Couldn't request check in. ${results.data.errors[0].message}`});
          }
          else{
            this.setState({transactions: results.data.data.checkInItem.transactions})
          }
        },
        error => {
          console.log(error);
          console.log(CHECKIN_ITEM);
          this.setState({errors: `Couldn't check in ${item}`});
        });
  }

  /**
   * Administrators can create items
   * @param {string} item: Name of the item being created
   * @param {string} quantity: Quantity available
   */
  createItem(item, quantity){
    const CREATE_ITEM = `
    mutation{
      createItem(authToken: "${this.state.authToken}", email: "${this.state.email}",
                 itemName: "${item}", quantity: ${quantity}){
        items{
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
          error => {
            console.log(error);
            console.log(CREATE_ITEM);
            this.setState({errors: `Couldn't create ${item}`});
          });
  }

  /**
   * Administrators can delete items
   * @param {string} item: Name of the item being deleted
   */
  deleteItem(item){
    const DELETE_ITEM = `
      mutation{
        deleteItem(itemName: "${item}", authToken: "${this.state.authToken}",
                   email:"${this.state.email}"){
          items{
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
          error => {
            console.log(error);
            console.log(DELETE_ITEM);
            this.setState({errors: `Couldn't delete ${item}`});
          });
  }

  /**
   * Verify that a user's authentication token and username (from localstorage) are valid.
   */
  verifyAuthentication(){
    const account = msalInstance.getAccount()
    if (account) {
      const authToken = Buffer.from(JSON.stringify(account.idToken)).toString("base64");
      this.updateAuthenticatedState(authToken, account.userName, account.name)
    } else {
      this.updateAuthenticatedState()
    }
  }

  /**
   * Updates the state when a token's validity is established
   * @param {string} authToken 
   * @param {string} username 
   * @param {boolean} isAdmin
   */
  updateAuthenticatedState(authToken=null, email=null, name=null){
    this.setState({authToken: authToken, email: email, name: name});
    //this.getAllTransactions();
    this.setState({loading: false});
  }

  /**
   * Allows user to log in
   */
  logIn(){
    msalInstance.loginPopup(msalRequestScope)
    .then(
      response => { window.location.reload() },
      error => { console.log(error) }
    )
  }

  /**
   * Allows user to log out.
   * In the backend, the valid token is blacklisted.
   */
  logOut(){
    msalInstance.logout()
  }

  render() {
    if(this.state.loading){
      return "Loading...";
    }
    return (
      <div className="App">
        <div className="errors" style={{display: this.state.errors.trim() === "" ? 'none' : 'block' }}>
          <AlertNotifications
            variant="error"
            message={this.state.errors}
          />
        </div>
        <header className="App-header">
            <div className="logo">
              <img src={logo} className="App-logo" alt="logo" />
              <p>Tech Cabinet Rental Platform</p>
            </div>
            <div className="login" style={{display: !this.state.email || !this.state.authToken ? "block" : "none" }}>
              <Button variant="contained" onClick={(e) => this.logIn()}>
                Log In
              </Button>
            </div>
            <div className="welcome" style={{display: this.state.email && this.state.authToken ? "block" : "none" }}>
              <p> Welcome, {this.state.name}! </p>
              <Button variant="contained" onClick={(e) => this.logOut()}>
                Log Out
              </Button>
            </div>
        </header>
        <div className="container">
          <h1>Information</h1>
          <p>Welcome to the Engineering Undergraduate Society's rental platform for the tech cabinet.</p>
          <p>To request an item, simply click on its name and follow the form instructions.</p>
          <p>Please contact Chris in the EUS Office (<b>McConnell room 7</b>) to collect your item.</p>
          <p>You are expected to return rented items within <b>five days</b> excluding week-ends.</p>
          <h1>Available Items</h1>
          <RentalTable tokenValidity={this.state.tokenValidity} results={this.state.results} deleteItem={this.deleteItem} requestItem={this.checkOutItem}/>
          <div className="form" style={{display: this.state.email && this.state.authToken ? "block" : "none" }}>
            <SimpleStyledTextField textFieldLabel1="item" textFieldLabel2="quantity" label="Add item" onClickEvent={this.createItem}/>
          </div>
          <br></br>
          <div className="transactions" style={{display: this.state.email && this.state.authToken > 0 ? "block" : "none" }}>
          <h1 style={{display: this.state.tokenValidity === 1 ? "block" : "none" }}> Your Requests </h1>
          <h1 style={{display: this.state.tokenValidity === 2 ? "block" : "none" }}> Request History </h1>
          <Table>
          <TableHead>
            <TableRow>
              <TableCell align="true">User Requesting Item</TableCell>
              <TableCell align="true">Item Requested</TableCell>
              <TableCell align="true">Date Requested</TableCell>
              <TableCell align="true">Date Accepted</TableCell>
              <TableCell align="true">Date Returned</TableCell>
              <TableCell align="true">Quantity Requested</TableCell>
              <TableCell align="true">Order Accepted?</TableCell>
              <TableCell align="true">User Who Accepted The Order</TableCell>
              {this.state.tokenValidity > 1 ? <TableCell align="true">Action</TableCell> : null}
            </TableRow>
          </TableHead>
          <TableBody>
            {this.state.transactions.map((row, index) => {
              return (
                <TableRow key={index}>
                  <TableCell align="true">{row.userRequestedId}</TableCell>
                  <TableCell align="true">{row.item}</TableCell>
                  <TableCell align="true">{row.dateRequested}</TableCell>
                  <TableCell align="true">{row.dateAccepted}</TableCell>
                  <TableCell align="true">{row.dateReturned}</TableCell>
                  <TableCell align="true">{row.requestedQuantity}</TableCell>
                  <TableCell align="true">{row.accepted ? "Yes" : "No"}</TableCell>
                  <TableCell align="true">{row.userAccepted}</TableCell>
                  {this.state.tokenValidity > 1 ?
                  <TableCell align="true">
                    {!row.accepted ? <Button onClick={() => this.acceptCheckoutRequest(row.userRequestedId, row.id, row.item) }>Accept</Button> : null}
                    {row.accepted && !row.returned ? <Button onClick={() => {this.checkInItem(row.item, row.id);}} >Check In</Button> : null}
                  </TableCell>
                  : null
                  }
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
