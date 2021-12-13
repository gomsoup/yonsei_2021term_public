import 'dart:async';
import 'dart:convert';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/http.dart' as http;
import 'package:http/retry.dart';


const APP_SWITCH_ARGENT_MODE = "APP_SWITCH_ARGENT_MODE";
const APP_SWITCH_NORMAL_MODE = "APP_SWITCH_NORMAL_MODE";
const DEVICE_PACKAGE_RECEIVED = "DEVICE_PACKAGE_RECEIVED";
const DEVICE_ALERT_ARGENT = "DEVICE_ALERT_ARGENT";

const APP_SWITCH_ARGENT_MODE_STRING = "앱에서 긴급 모드로 전환하였습니다.";
const APP_SWITCH_NORMAL_MODE_STRING = "앱에서 일반 모드로 전환하였습니다.";
const DEVICE_PACKAGE_RECEIVED_STRING = "택배가 도착하였습니다.";
const DEVICE_ALERT_ARGENT_STRING = "장치에서 긴급 상황을 감지하였습니다.";

class PackageInfo{
  final String date;
  final String data;

  PackageInfo({required this.date, required this.data});

  factory PackageInfo.fromJson(Map<String, dynamic> json){
    if(json['data'] == APP_SWITCH_ARGENT_MODE){
      json['data'] = APP_SWITCH_ARGENT_MODE_STRING;
    }
    else if (json['data'] == APP_SWITCH_NORMAL_MODE){
      json['data'] = APP_SWITCH_NORMAL_MODE_STRING;
    }
    else if (json['data'] == DEVICE_PACKAGE_RECEIVED){
      json['data'] = DEVICE_PACKAGE_RECEIVED_STRING;
    }
    else if (json['data'] == DEVICE_ALERT_ARGENT){
      json['data'] = DEVICE_ALERT_ARGENT_STRING;
    }

    return PackageInfo(
      date: json['date'],
      data: json['data'],
    );
  }
}

Future<List<PackageInfo>> fetchPackageInfo() async{
  final client = RetryClient(http.Client(), retries: 5);
  http.Response? res;

  var i = 1;
  try{
    res = await client.get(
      Uri.parse("http://server.gomsoup.com:9949/communicate/app"),
    );

    if(res.statusCode != 200){
      print(res.body);
      throw 1;
    }
  }catch(e){
    Fluttertoast.showToast(
        msg: "Failed to fetch package info from server",
        toastLength: Toast.LENGTH_SHORT,
        timeInSecForIosWeb:  1
    );
    i++;
  }

  if(res!.statusCode == 200){
    List list = json.decode(res.body)['datas'];
    List<PackageInfo> ret = list.map((data)=>PackageInfo.fromJson(data)).toList();
    print(ret);
    return ret;
  }else{
    Fluttertoast.showToast(
        msg: "Failed to fetch package info from server",
        toastLength: Toast.LENGTH_SHORT,
        timeInSecForIosWeb:  1
    );
    throw Exception('Fail to fetch package data');
  }
}

void postArgentMode() async{
  final client = RetryClient(http.Client(), retries: 5);
  var i = 1;
  try{
    var res = await client.post(
      Uri.parse("http://server.gomsoup.com:9949/communicate/app"),
      headers: <String, String>{
      'Content-Type' : 'application/x-www-form-urlencoded',
      },
      body: "message=1",
    );

    if(res.statusCode != 200){
      print(res.body);
      throw 1;
    }
  }catch(e){
    Fluttertoast.showToast(
        msg: "Failed to post argent info to server. retrying $i..",
        toastLength: Toast.LENGTH_SHORT,
        timeInSecForIosWeb:  1
    );
    i++;
  }finally{
    print('post argent done');
  }
}

void postNormalMode() async{
  final client = RetryClient(http.Client(), retries: 5);
  var i = 1;
  try{
    var res = await client.post(
      Uri.parse("http://server.gomsoup.com:9949/communicate/app"),
      headers: <String, String>{
        'Content-Type' : 'application/x-www-form-urlencoded',
      },
      body: "message=2",
    );

    if(res.statusCode != 200){
      print(res.body);
      throw 1;
    }
  }catch(e){
    Fluttertoast.showToast(
        msg: "Failed to post argent info to server. retrying $i..",
        toastLength: Toast.LENGTH_SHORT,
        timeInSecForIosWeb:  1
    );
    i++;
  }finally{
    print('post argent done');
  }
}