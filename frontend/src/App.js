import React, { Component } from 'react';
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
//import { Button, Image, View, Text } from 'react-native'; TODO: For some reason, this package isn't getting imported ??
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

function createData(name, quantity, last_checkout, checked_out_by) {
  return { name, quantity, last_checkout, checked_out_by };
}

// TODO: Data should be from a DB
const rows = [
  createData('VGA to HDMI cable', 2, '1PM', 'Andrei'),
  createData('iPhone Charger', 1, '6PM', 'Andrei'),
  createData('Android Charger', 0, '3PM', 'Andrei'),
];

function SimpleButton(props) {
  const { classes } = props;
  return (
    <Button variant="contained" className={classes.button}>
    Log In
    </Button>
  );
}

// TODO: This one should be maybe in a separate file ...?
function SimpleTable(props) {
  const { classes } = props;

  return (
    <Paper className={classes.root}>
      <Table className={classes.table}>
        <TableHead>
          <TableRow>
            <TableCell>Tech Item</TableCell>
            <TableCell numeric>Quantity</TableCell>
            <TableCell numeric>Last Checkout At...</TableCell>
            <TableCell numeric>Checked Out By</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map(row => {
            return (
              <TableRow key={row.id}>
                <TableCell component="th" scope="row">
                  {row.name}
                </TableCell>
                <TableCell numeric>{row.quantity}</TableCell>
                <TableCell numeric>{row.last_checkout}</TableCell>
                <TableCell numeric>{row.checked_out_by}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Paper>
  );
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

const LoginButton = withStyles(buttonStyles)(SimpleButton);
const RentalTable = withStyles(tableStyles)(SimpleTable);
const TextFields = withStyles(textBoxStyles)(SimpleTextFields);


class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
            <div class="logo">
              <img src={logo} className="App-logo" alt="logo" />
              <p>Tech Cabinet Rental Platform</p>
            </div>
            <div class="login">
              <TextFields/>
              <LoginButton/>
            </div>
        </header>
        <div class="container">
          <h1>Available Items</h1>
          <RentalTable/>
        </div>
      </div>
    );
  }
}

export default App;
