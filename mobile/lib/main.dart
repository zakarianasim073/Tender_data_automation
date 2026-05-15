import 'package:flutter/material.dart';

void main() => runApp(const TenderApp());

class TenderApp extends StatelessWidget {
  const TenderApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Tender Mobile',
      home: Scaffold(
        appBar: AppBar(title: const Text('Tender Submission (Offline Ready)')),
        body: const Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('• Offline form cache enabled (local-first workflow)'),
              Text('• BOQ mismatch alert sync after reconnect'),
              Text('• Mobile submission checklist and audit preview'),
            ],
          ),
        ),
      ),
    );
  }
}
