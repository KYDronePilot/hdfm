import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:settings_ui/settings_ui.dart';

void main() {
  runApp(Hdfm());
}

// class MyApp extends StatelessWidget {
//   // This widget is the root of your application.
//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       title: 'Flutter Demo',
//       theme: ThemeData(
//         // This is the theme of your application.
//         //
//         // Try running your application with "flutter run". You'll see the
//         // application has a blue toolbar. Then, without quitting the app, try
//         // changing the primarySwatch below to Colors.green and then invoke
//         // "hot reload" (press "r" in the console where you ran "flutter run",
//         // or simply save your changes to "hot reload" in a Flutter IDE).
//         // Notice that the counter didn't reset back to zero; the application
//         // is not restarted.
//         primarySwatch: Colors.blue,
//       ),
//       home: MyHomePage(title: 'Flutter Demo Home'),
//     );
//   }
// }

class Hdfm extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HDFM',
      theme: ThemeData(primarySwatch: Colors.green),
      home: HdfmHomePage(),
    );
  }
}

class StationDetailsPage extends StatefulWidget {
  // StationDetailsPage({this.artist});
  StationDetailsPage({
    Key? key,
    required this.artist,
    required this.title,
  }) : super(key: key);

  final String artist;
  final String title;

  @override
  _StationDetailsPageState createState() => _StationDetailsPageState();
}

class _StationDetailsPageState extends State<StationDetailsPage> {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.all(16.0),
      child: Table(
        border: TableBorder.all(),
        children: [
          TableRow(
            children: [
              Container(
                alignment: Alignment.centerRight,
                child: Text('Artist'),
              ),
              Container(
                child: Text(widget.artist),
              )
            ],
          ),
          TableRow(
            children: [
              Container(
                alignment: Alignment.centerRight,
                child: Text('Title'),
              ),
              Container(
                child: Text(widget.title),
              )
            ],
          ),
        ],
      ),
    );
  }
}

class WeatherMapPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Image.network(
        'https://github.com/KYDronePilot/hdfm/raw/master/img/weather_map.png');
  }
}

class TrafficMapPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Image.network(
        'https://github.com/KYDronePilot/hdfm/raw/master/img/traffic_map.png');
  }
}

class AlbumArtworkPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Text('AlbumArtworkPage');
  }
}

class SettingsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.all(16.0),
      child: Table(
        border: TableBorder.all(),
        children: [
          TableRow(
            children: [
              Container(
                alignment: Alignment.centerRight,
                child: Text('test'),
              ),
              Container(
                child: Text(
                    'test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test'),
              )
            ],
          ),
          TableRow(
            children: [
              Container(
                alignment: Alignment.centerRight,
                child: Text('test'),
              ),
              Container(
                child: Text('test'),
              )
            ],
          ),
        ],
      ),
    );
  }
}

class HdfmHomePage extends StatefulWidget {
  // MyHomePage({Key? key, required this.title}) : super(key: key);

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  // final String title;

  @override
  _HdfmHomePageState createState() => _HdfmHomePageState();
}

class _HdfmHomePageState extends State<HdfmHomePage> {
  bool isRunning = false;
  Process? hdfmProc;
  String? artist;
  String? title;

  void handleLine(String line) {
    final artistRegex = RegExp(r'Artist: (.*?)$');
    final artistMatch = artistRegex.firstMatch(line);
    if (artistMatch != null) {
      setState(() {
        artist = artistMatch.group(1);
      });
    }
    final titleRegex = RegExp(r'Title: (.*?)$');
    final titleMatch = titleRegex.firstMatch(line);
    if (titleMatch != null) {
      setState(() {
        title = titleMatch.group(1);
      });
    }
  }

  void toggleRun() async {
    if (!isRunning) {
      hdfmProc = await Process.start('nrsc5', ['98.1', '0']);
      hdfmProc!.stderr
          .transform(const Utf8Decoder())
          .transform(const LineSplitter())
          .forEach(handleLine);
      // var output = await Process.run('ls', ['-l']);
      // await hdfmProc!.exitCode;
      // print(proc.stdout.transform(utf8.decoder).toString());
      setState(() {
        isRunning = true;
      });
    } else if (hdfmProc != null) {
      hdfmProc!.kill();
      hdfmProc = null;
      print('Stopped');
      setState(() {
        isRunning = false;
        artist = '';
        title = '';
      });
    }
  }

  Widget build(context) {
    return DefaultTabController(
      length: 5,
      child: Scaffold(
        appBar: AppBar(
          title: Text('HDFM'),
          bottom: TabBar(
            isScrollable: false,
            tabs: [
              Tab(text: 'Station Details'),
              Tab(text: 'Weather Map'),
              Tab(text: 'Traffic Map'),
              Tab(text: 'Album Artwork'),
              Tab(text: 'Settings'),
            ],
          ),
        ),
        body: SafeArea(
          bottom: false,
          child: TabBarView(
            children: [
              StationDetailsPage(
                artist: artist ?? '',
                title: title ?? '',
              ),
              WeatherMapPage(),
              TrafficMapPage(),
              AlbumArtworkPage(),
              SettingsPage(),
            ],
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: toggleRun,
          child: Icon(isRunning ? Icons.stop : Icons.play_arrow),
        ),
      ),
    );
  }
}

// class _MyHomePageState extends State<MyHomePage> {
//   int _counter = 0;

//   void _incrementCounter() {
//     setState(() {
//       // This call to setState tells the Flutter framework that something has
//       // changed in this State, which causes it to rerun the build method below
//       // so that the display can reflect the updated values. If we changed
//       // _counter without calling setState(), then the build method would not be
//       // called again, and so nothing would appear to happen.
//       _counter++;
//     });
//   }

//   @override
//   Widget build(BuildContext context) {
//     // This method is rerun every time setState is called, for instance as done
//     // by the _incrementCounter method above.
//     //
//     // The Flutter framework has been optimized to make rerunning build methods
//     // fast, so that you can just rebuild anything that needs updating rather
//     // than having to individually change instances of widgets.
//     return Scaffold(
//       appBar: AppBar(
//         // Here we take the value from the MyHomePage object that was created by
//         // the App.build method, and use it to set our appbar title.
//         title: Text(widget.title),
//       ),
//       body: Center(
//         // Center is a layout widget. It takes a single child and positions it
//         // in the middle of the parent.
//         child: Column(
//           // Column is also a layout widget. It takes a list of children and
//           // arranges them vertically. By default, it sizes itself to fit its
//           // children horizontally, and tries to be as tall as its parent.
//           //
//           // Invoke "debug painting" (press "p" in the console, choose the
//           // "Toggle Debug Paint" action from the Flutter Inspector in Android
//           // Studio, or the "Toggle Debug Paint" command in Visual Studio Code)
//           // to see the wireframe for each widget.
//           //
//           // Column has various properties to control how it sizes itself and
//           // how it positions its children. Here we use mainAxisAlignment to
//           // center the children vertically; the main axis here is the vertical
//           // axis because Columns are vertical (the cross axis would be
//           // horizontal).
//           mainAxisAlignment: MainAxisAlignment.center,
//           children: <Widget>[
//             Text(
//               'You have pushed the button this many times:',
//             ),
//             Text(
//               '$_counter',
//               style: Theme.of(context).textTheme.headline4,
//             ),
//           ],
//         ),
//       ),
//       floatingActionButton: FloatingActionButton(
//         onPressed: _incrementCounter,
//         tooltip: 'Increment',
//         child: Icon(Icons.add),
//       ), // This trailing comma makes auto-formatting nicer for build methods.
//     );
//   }
// }
