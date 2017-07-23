import React, { Component } from 'react';
import logo from './logo.png';
import './App.css';

import GoogleLogin from 'react-google-login';


function generateUUID () { // Public Domain/MIT
  var d = new Date().getTime();
  if (typeof performance !== 'undefined' && typeof performance.now === 'function'){
    d += performance.now(); //use high-precision timer if available
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    var r = (d + Math.random() * 16) % 16 | 0;
    d = Math.floor(d / 16);
    return (c === 'x' ? r : (r & (0x3 | 0x8))).toString(16);
  });
}


class App extends Component {

  constructor() {
    super();

    this.state = {
      loggedIn: false,
    };

    this.tasks = {
    };

    this.loginSuccess = this.loginSuccess.bind(this);
    this.loginFailure = this.loginFailure.bind(this);

  };

  loginSuccess(response) {
    window.login = response;

    this.ws = new WebSocket('/controller');
    this.ws.onmessage = evt => {
      var msg = JSON.parse(evt.data);
      if (msg.error) {
        console.log("Error on task " + msg.uuid + ": " + msg.error.reason);
      } else if (msg.data) {
        this.tasks[msg.uuid].onmessage(this, msg.data);
      }
      if (msg.end) delete this.tasks[msg.uuid];
    };

    this.ws.onopen = evt => {
      var taskId = generateUUID();

      this.tasks[taskId] = {
        onmessage: function (app, data) {
          app.setState({loggedIn: data.logged});
        }
      };

      this.ws.send(JSON.stringify({
        uuid: taskId,
        action: "login",
        args: {
          token: response.getAuthResponse().id_token
        }
      }));
    };

    this.ws.onmessage = this.ws.onmessage.bind(this);
    this.ws.onopen = this.ws.onopen.bind(this);

  };

  loginFailure(response) {
    this.setState({loggedIn: false});
  };

  render() {
    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
        </div>
        <p className="App-intro">
        </p>
        { !this.state.loggedIn &&
          <GoogleLogin
              clientId="109000862034-kn654663dt4jg7hpc9ugj5ldddhousl7.apps.googleusercontent.com"
              buttonText="Login"
              onSuccess={this.loginSuccess}
              onFailure={this.loginFailure}
              offline={false}
          /> }
      </div>
    );
  }
}

export default App;
