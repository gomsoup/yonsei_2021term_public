import 'package:app/server_connection.dart';
import 'package:app/push_notification.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_speed_dial/flutter_speed_dial.dart';

void main() async{
  await init();
  runApp(const MyApp());
}

Future init() async{
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Startup Name Generator',
      theme: ThemeData(
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Colors.black,
        ),
      ),

      home: Package(),
    );
  }
}

class Package extends StatefulWidget{
  @override
  State<StatefulWidget> createState() {
    return _PackageState();
  }
}

class _PackageState extends State<Package>{
  late Future<List<PackageInfo>> packageInfo;

  void _changeData(String msg) {
    refreshPackageInfo();
  }

  @override
  void initState(){
    final firebaseMessaging = FCM();
    firebaseMessaging.setNotification();
    firebaseMessaging.streamCtl.stream.listen(_changeData);

    packageInfo = fetchPackageInfo();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
          title: const Text('택배 알리미'),
      ),
      body: Center(
          child: FutureBuilder<List<PackageInfo>>(
            future: packageInfo,
            builder: (context, snapshot){
              return RefreshIndicator(
                  child: _listPackageInfo(snapshot),
                  onRefresh: refreshPackageInfo,
              );

            }),
        ),
      floatingActionButton: SpeedDial(
        animatedIcon: AnimatedIcons.menu_close,
        animatedIconTheme: IconThemeData(size: 22.0),
        curve: Curves.bounceIn,
        overlayOpacity: 0.5,
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        elevation: 8.0,
        shape: CircleBorder(),
        children:[
          SpeedDialChild(
            child: Icon(Icons.warning_amber_rounded),
            backgroundColor: Colors.pink,
            foregroundColor: Colors.white,
            label: '긴급모드 전환',
            onTap: postArgentMode,
          ),
          SpeedDialChild(
            child: Icon(Icons.play_circle_outline),
            label: '일반모드 전환',
            onTap: postNormalMode,
          )
        ]

      )
    );
  }

  Widget _listPackageInfo(AsyncSnapshot snapshot){
    if(snapshot.connectionState == ConnectionState.waiting) {
      return Center(child: CircularProgressIndicator());
    } else if (snapshot.hasError) {
      return Text('${snapshot.error}');
    }

    List<PackageInfo> list = snapshot.data ?? [];
    return ListView.builder(
        itemCount: list.length,
        itemBuilder: (context, i){
          PackageInfo p = list[i];
          return ListTile(
            title: Text(
              p.date,
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Text(
              p.data,
            ),
          );
        }
    );
  }

  Future<void> refreshPackageInfo() async{
    List<PackageInfo>? freshPackageInfo = await fetchPackageInfo();

    if(freshPackageInfo != null) {
      setState(() {
        packageInfo = Future.value(freshPackageInfo);
      });
    }
  }
}