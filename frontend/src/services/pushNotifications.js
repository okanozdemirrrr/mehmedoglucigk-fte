import { Capacitor } from '@capacitor/core';
import api from './api';
import { isFirebaseConfigured, requestWebFcmToken } from '../firebase';

let nativeListenersReady = false;

/** Android/iOS — listener'lar register()'dan ÖNCE kurulmalı */
const setupNativePushListeners = async () => {
  if (nativeListenersReady || !Capacitor.isNativePlatform()) {
    return;
  }

  const { PushNotifications } = await import('@capacitor/push-notifications');

  await PushNotifications.addListener('registration', async (token) => {
    const authToken = localStorage.getItem('token');
    if (!authToken || !token.value) {
      return;
    }
    try {
      await api.post('accounts/fcm-token/', { fcm_token: token.value });
    } catch (error) {
      console.warn('FCM token backend kaydı başarısız:', error);
    }
  });

  await PushNotifications.addListener('registrationError', (error) => {
    console.warn('Push kayıt hatası:', error);
  });

  await PushNotifications.addListener('pushNotificationReceived', (notification) => {
    console.info('Push alındı (uygulama açık):', notification.title, notification.body);
  });

  await PushNotifications.addListener('pushNotificationActionPerformed', (action) => {
    const data = action.notification?.data || {};
    if (data.order_id && typeof window !== 'undefined') {
      const role = JSON.parse(localStorage.getItem('user') || '{}').role;
      const path = role === 'DEALER' ? '/bayi/siparisler' : '/admin/siparisler';
      window.location.href = path;
    }
  });

  nativeListenersReady = true;
};

const ensureNativePermission = async () => {
  const { PushNotifications } = await import('@capacitor/push-notifications');
  let { receive } = await PushNotifications.checkPermissions();

  if (receive === 'prompt' || receive === 'prompt-with-rationale') {
    ({ receive } = await PushNotifications.requestPermissions());
  }

  return receive === 'granted';
};

/** FCM token al ve Django'ya kaydet */
export const registerFcmToken = async () => {
  const authToken = localStorage.getItem('token');
  if (!authToken) {
    return null;
  }

  if (Capacitor.isNativePlatform()) {
    await setupNativePushListeners();

    const granted = await ensureNativePermission();
    if (!granted) {
      return null;
    }

    const { PushNotifications } = await import('@capacitor/push-notifications');
    await PushNotifications.register();
    return 'native-registered';
  }

  if (isFirebaseConfigured()) {
    const fcmToken = await requestWebFcmToken();
    if (!fcmToken) {
      return null;
    }
    await api.post('accounts/fcm-token/', { fcm_token: fcmToken });
    return fcmToken;
  }

  return null;
};

/** Uygulama açılışında native push dinleyicilerini başlat */
export const initPushNotifications = async () => {
  if (!Capacitor.isNativePlatform()) {
    return;
  }

  await setupNativePushListeners();

  if (localStorage.getItem('token')) {
    await registerFcmToken();
  }
};
