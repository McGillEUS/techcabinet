import * as Msal from "msal";

const msalInstance = new Msal.UserAgentApplication({
  auth: {
    clientId: "e1aead66-c339-4a1f-9170-30a03f40367a",
    authority: "https://login.microsoftonline.com/cd319671-52e7-4a68-afa9-fcf8f89f09ea",
    redirectUri: "http://localhost:3000/"
  },
  cache: {
      cacheLocation: "localStorage",
      storeAuthStateInCookie: true
  }
});

export { msalInstance }
