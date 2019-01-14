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

// TODO: Move all these styles elsewhere!!!
const buttonStyles = theme => ({
  button: {
    margin: theme.spacing.unit,
  },
  input: {
    display: 'none',
  },
});

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
  container: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  textField: {
    marginLeft: theme.spacing.unit,
    marginRight: theme.spacing.unit,
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

class SimpleButton extends React.Component{
  render(){
    return (
      <Button variant="contained" className={this.props.classes.button} onClick={this.props.onClickEvent}>
        {this.props.label}
      </Button>
    );
  }
}

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

class SimpleTextFields extends React.Component {
  state = {
    username: '',
    password: ''
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
          id="filled-name"
          label="Username"
          className={classes.textField}
          value={this.state.username}
          onChange={this.handleChange('username')}
          margin="normal"
          variant="filled"
        />
        <TextField
          id="filled-name"
          label="Password"
          className={classes.textField}
          value={this.state.password}
          onChange={this.handleChange('password')}
          margin="normal"
          variant="filled"
        />
      </form>
    );
  }
}

SimpleTextFields.propTypes = {
  classes: PropTypes.object.isRequired,
};

SimpleTable.propTypes = {
  classes: PropTypes.object.isRequired
};

SimpleButton.propTypes = {
  classes: PropTypes.object.isRequired,
};

const BasicButton = withStyles(buttonStyles)(SimpleButton);
const RentalTable = withStyles(tableStyles)(SimpleTable);
const TextFields = withStyles(textBoxStyles)(SimpleTextFields);

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

  checkOutItem() {
    let name = "tomato";
    let quantity = 1;
    let checkedOutBy = "Andrei";
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

  checkInItem() {
    let name = "tomato";
    let quantity = 1;
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

  render() {
    return (
      <div className="App">
        <header className="App-header">
            <div className="logo">
              <img src={logo} className="App-logo" alt="logo" />
              <p>Tech Cabinet Rental Platform</p>
            </div>
            <div className="login">
              <TextFields/>
              <BasicButton label="LOG IN"/>
            </div>
        </header>
        <div className="container">
          <h1>Available Items</h1>
          <RentalTable results={this.state.results}/>
          <BasicButton label="+" onClickEvent={this.checkInItem} />
          <BasicButton label="-" onClickEvent={this.checkOutItem} />
        </div>
      </div>
    );
  }
}

export default App;
