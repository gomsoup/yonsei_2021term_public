import 'dart:async';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

Future<void> onBackgroundMessage(RemoteMessage message) async {
  await Firebase.initializeApp();

  if (message.data.containsKey('data')) {
    final data = message.data['data'];
  }

  if (message.data.containsKey('title')) {
    final notification = message.data['title'];
  }
}

// FCM Controller class
// 현재는 onBackground에서만 notify를 실행
class FCM {
  final _firebaseMessaging = FirebaseMessaging.instance;

  final streamCtl = StreamController<String>.broadcast();
  final titleCtl = StreamController<String>.broadcast();
  final bodyCtl = StreamController<String>.broadcast();

  setNotification() {
    FirebaseMessaging.onBackgroundMessage(onBackgroundMessage);
    FirebaseMessaging.onMessage.listen((message) async {
      if (message.data.containsKey('data')) {
        streamCtl.sink.add(message.data['data']);
      }
      if (message.data.containsKey('title')) {
        streamCtl.sink.add(message.data['title']);
      }

      titleCtl.sink.add(message.notification!.title!);
      bodyCtl.sink.add(message.notification!.body!);
    });

    final token =
        _firebaseMessaging.getToken().then((value) => print('Token: $value'));
  }

  dispose() {
    streamCtl.close();
    bodyCtl.close();
    titleCtl.close();
  }
}
