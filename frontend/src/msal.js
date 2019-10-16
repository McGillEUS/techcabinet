import * as Msal from "msal";

const msalInstance = new Msal.UserAgentApplication({
  /* [NOTE]: The app does not work unless...
  * -> ClientID is specified
  * -> authority URL includes ClientID at the end (microsoftonline.com/<CLIENT_ID>)
  * This information is available in Azure, contact Andrei to gain access to it.
  * [DEPLOY TODO]: redirectURI needs to be changed to https://rental.mcgilleus.ca/ for the live version
  */
  auth: {
    clientId: "",
    authority: "https://login.microsoftonline.com/",
    redirectUri: "http://localhost:3000/"
  },
  cache: {
      cacheLocation: "localStorage",
      storeAuthStateInCookie: true
  }
});

export { msalInstance }
