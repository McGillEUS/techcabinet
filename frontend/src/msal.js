import * as Msal from "msal";

const msalInstance = new Msal.UserAgentApplication({
  auth: {
    clientId: "",
    authority: "https://login.microsoftonline.com",
    redirectUri: "http://localhost:3000/"
  },
  cache: {
      cacheLocation: "localStorage",
      storeAuthStateInCookie: true
  }
});

export { msalInstance }
