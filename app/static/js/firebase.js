// Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/12.19.0/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.19.0/firebase-analytics.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
  const firebaseConfig = {
    apiKey: "AIzaSyAVAHJ55vJB8BTyJYXgWKmd-6b9ZJmIuI8",
    authDomain: "authentication-ae570.firebaseapp.com",
    projectId: "authentication-ae570",
    storageBucket: "authentication-ae570.firebasestorage.app",
    messagingSenderId: "210543750432",
    appId: "1:210543750432:web:31e720fc949e10f87b7b45",
    measurementId: "G-ZPK82TBCRW"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);