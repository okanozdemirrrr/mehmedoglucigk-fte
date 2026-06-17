import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, isSupported } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

let app = null;

export const getFirebaseApp = () => {
  if (!app && firebaseConfig.apiKey && firebaseConfig.projectId) {
    app = initializeApp(firebaseConfig);
  }
  return app;
};

export const isFirebaseConfigured = () =>
  Boolean(firebaseConfig.apiKey && firebaseConfig.projectId);

/** Web tarayıcısında FCM token alır (izin gerekir). */
export const requestWebFcmToken = async () => {
  if (!isFirebaseConfigured()) {
    console.warn('Firebase yapılandırması eksik (VITE_FIREBASE_* env).');
    return null;
  }

  const supported = await isSupported();
  if (!supported) {
    return null;
  }

  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    return null;
  }

  const firebaseApp = getFirebaseApp();
  const messaging = getMessaging(firebaseApp);
  const vapidKey = import.meta.env.VITE_FIREBASE_VAPID_KEY;

  const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');

  return getToken(messaging, {
    vapidKey,
    serviceWorkerRegistration: registration,
  });
};
