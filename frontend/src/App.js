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
import { msalInstance } from './msal.js'

import './App.css';

// [DEPLOY TODO]: baseURL needs to be changed to 'https://rental.mcgilleus.ca/graphql'
// The app will not run unless the baseURL points to where the Python back-end is running.
const axiosGraphQL = axios.create({
  baseURL: 'http://localhost:4293/graphql',
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
  * `authLevel`: Level of validity of a token (0: invalid, 1: user, 2: admin)
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
      authLevel: 0,
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
    this.reserveItem = this.reserveItem.bind(this);
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
  getAllItems(label=null) {
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

  axiosGraphQL
    .post('', { query: GET_ITEMS })
    .then(results => {
      this.setState({results: results.data.data.allItems.edges
        .filter(result => label == null ? true : result.node.name.includes(label))
        .map(result => result.node)})
      },
      error => {console.log(error); console.log(GET_ITEMS)});
  };

  /**
   * Mutation because I had a hard time figuring out how to return different things for different auth levels with a query
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
        adminAccepted,
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
    .post('', { query: GET_TRANSACTIONS })
    .then(
      results => {
        this.setState({
          transactions: results.data.data.showTransactions.transactions
        })
      },
      error => {
        console.log(error);
        this.setState({errors: "Couldn't load all transactions."})
      });
  }

  /**
   * Creates a reservation for a user.
   * If  the optional fields are not provided, the user must currently be authenticated.
   * @param {string} itemName: Name of the item getting checked out
   * @param {int} quantity: How much of the object is getting checked out
   * @param {string} studentID: Student ID for this user.
   */
  reserveItem(itemName, quantity, studentID){
    studentID = studentID || "";

    const RESERVE_ITEM = `
      mutation{
        reserveItem(email: "${this.state.email}", studentId: "${studentID}",
                    authToken: "${this.state.authToken}", quantity: ${quantity},
                    itemName:"${itemName}"){
          items{
            name
          }
        }
      }
    `

    axiosGraphQL
      .post('', { query: RESERVE_ITEM })
      .then(
        results => {
          if (results.data.errors && results.data.errors.length > 0){
            this.setState({errors: `Checkout request unsuccessful. ${results.data.errors[0].message}`});
          }
          else{
            this.setState({results: results.data.data.reserveItem.items});
            window.location.reload();
          }
        },
        error => {
          this.setState({errors: `Couldn't check out ${itemName}. ${error}`});
        }
      );
  }

  /**
   * Administrators accept the reservations of normal users & check out the item
   * @param {string} transactionId: ID of the transaction being accepted
   * @param {string} item: Name of the item getting checked out
   */
  checkOutItem(transactionId, item) {
    const ACCEPT_CHECKOUT_REQUEST = `
    mutation{
      checkOutItem(transactionId: "${transactionId}", item: "${item}",
                   adminEmail: "${this.state.email}", authToken: "${this.state.authToken}"){
        transactions{
          id,
          accepted,
          returned,
          adminAccepted,
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
    .then(
      results => {
        if (results.data.errors && results.data.errors.length > 0){
          this.setState({errors: `Couldn't accept checkout request. ${results.data.errors[0].message}`});
        }
        else{
          this.setState({transactions: results.data.data.checkOutItem.transactions});
        }
      },
      error => {
        this.setState({errors: `Couldn't accept check out for ${item}. ${error}`});
      }
    );
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
                  adminEmail: "${this.state.email}", authToken: "${this.state.authToken}"){
        transactions{
          id,
          accepted,
          returned,
          adminAccepted,
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
        if (results.data.errors && results.data.errors.length > 0){
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
      }
    );
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
    .then(
      results => {
        if (results.data.errors && results.data.errors.length > 0){
          this.setState({errors: `Creation request unsuccessful. ${results.data.errors[0].message}`});
        }
        else{
          this.setState({results: results.data.data.createItem.items});
          window.location.reload();
        }
      },
      error => {
        console.log(error);
        console.log(CREATE_ITEM);
        this.setState({errors: `Couldn't create ${item}`});
      }
    );
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
    .then(results => {
        if (results.data.errors && results.data.errors.length > 0){
          this.setState({errors: `Delete request unsuccessful. ${results.data.errors[0].message}`});
        }
        else{
          this.setState({results: results.data.data.deleteItem.items});
          window.location.reload();
        }
      },
      error => {
        console.log(error);
        console.log(DELETE_ITEM);
        this.setState({errors: `Couldn't delete ${item}`});
      });
  }


  /**
   * Verify that a user's authentication token and username (from localstorage) are valid.
   * Also updates state to track user's authentication status
   */
  verifyAuthentication(){
    const account = msalInstance.getAccount()
    if (account) {
      msalInstance.acquireTokenSilent(msalRequestScope)
        .then(
          response => this.updateAuthenticatedState(response.accessToken, account.userName, account.name)
        )
    } else {
      this.updateAuthenticatedState();
    }
  }

  /**
   * Updates the state when a token's validity is established
   * @param {string} authToken 
   * @param {string} username 
   * @param {boolean} isAdmin
   */
  updateAuthenticatedState(authToken=null, email=null, name=null){
    const AUTH_LEVEL = `
      mutation{
        authenticationLevel(
          authToken: "${authToken}",
          email: "${email}")
        {
          level
        }
      }
    `
    axiosGraphQL
    .post('', { query: AUTH_LEVEL })
    .then(
      results => {
        if (results.data.data){
          this.setState({
            authToken: authToken,
            email: email,
            name: name,
            authLevel: results.data.data.authenticationLevel.level,
            loading: false
          });
          this.getAllTransactions();
        } else {
          if (results.data.errors && results.data.errors.length > 0){
            this.setState({errors: `Error updating login information. ${results.data.errors[0].message}`});
          } else {
            this.setState({errors: `Error updating login information.`});
          }
        }
      },
      error => {
        console.log(error);
        this.setState({errors: `Couldn't log in. ${error}`, loading: false});
      }
    );
  }

  /**
   * Allows user to log in
   */
  logIn(){
    msalInstance.loginPopup(msalRequestScope)
    .then(
      response => { window.location.reload(); },
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
              <p>EUS Rental Platform</p>
            </div>
            <div className="login" style={{display: !this.state.email && !this.state.authToken ? "block" : "none" }}>
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
        <div class="tab">
          <Button class="tablinks" onClick={() => this.getAllItems()}>All</Button>
          <Button class="tablinks" onClick={() => this.getAllItems('[BBQ]')}>Barbecue</Button>
          <Button class="tablinks" onClick={() => this.getAllItems('[TECH]')}>Tech Cabinet</Button>
        </div>
        <div className="container">
          <h1>Information</h1>
          <p>Welcome to the Engineering Undergraduate Society's rental platform.</p>
          <p>To request an item, simply click on its name and follow the form instructions.</p>
          <p>Please contact Chris in the EUS Office (<b>McConnell room 7</b>) to collect your item.</p>
          <p>You are expected to return rented items within <b>five days</b> excluding week-ends.</p>
          <h1>Available Items</h1>
          <RentalTable tokenValidity={this.state.authLevel} results={this.state.results} deleteItem={this.deleteItem} reserveItem={this.reserveItem}/>
          <div className="form" style={{display: this.state.email && this.state.authToken && this.state.authLevel > 1 ? "block" : "none" }}>
            <SimpleStyledTextField textFieldLabel1="item" textFieldLabel2="quantity" label="Add item" onClickEvent={this.createItem}/>
          </div>
          <br></br>
          <div className="transactions" style={{display: this.state.email && this.state.authLevel > 0 ? "block" : "none" }}>
          <h1 style={{display: this.state.authLevel === 1 ? "block" : "none" }}> Your Requests </h1>
          <h1 style={{display: this.state.authLevel === 2 ? "block" : "none" }}> Request History </h1>
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
              {this.state.authLevel > 1 ? <TableCell align="true">Action</TableCell> : null}
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
                  <TableCell align="true">{row.adminAccepted}</TableCell>
                  {this.state.authLevel > 1 ?
                  <TableCell align="true">
                    {!row.accepted ? <Button onClick={() => this.checkOutItem(row.id, row.item) }>Accept</Button> : null}
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
