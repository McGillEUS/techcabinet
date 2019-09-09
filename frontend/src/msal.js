import * as Msal from "msal";

const msalInstance = new Msal.UserAgentApplication({
  auth: {
    clientId: "",
    authority: "",
    redirectUri: "http://localhost:3000/"
  },
  cache: {
      cacheLocation: "localStorage",
      storeAuthStateInCookie: true
  }
});

export { msalInstance }
