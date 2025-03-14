import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Detector de Objetos',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  File? _image;
  final ImagePicker _picker = ImagePicker();
  String _caption = "No hay descripción disponible";
  bool _isLoading = false;
  
  // Dirección de tu API - cambia esto por la URL donde tengas desplegado tu servicio
  final String apiUrl = "http://192.168.1.8:8000/caption"; // Reemplaza con tu IP o dominio

  Future<void> _takePhoto() async {
    final XFile? photo = await _picker.pickImage(source: ImageSource.camera);
    
    if (photo != null) {
      setState(() {
        _image = File(photo.path);
        _caption = "Procesando imagen...";
        _isLoading = true;
      });
      
      await _sendImageToApi();
    }
  }

  Future<void> _pickImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    
    if (image != null) {
      setState(() {
        _image = File(image.path);
        _caption = "Procesando imagen...";
        _isLoading = true;
      });
      
      await _sendImageToApi();
    }
  }

  Future<void> _sendImageToApi() async {
    try {
      // Crear una solicitud multipart para enviar la imagen
      var request = http.MultipartRequest('POST', Uri.parse(apiUrl));
      
      // Añadir la imagen al request
      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          _image!.path,
        ),
      );
      
      // Enviar la solicitud
      var response = await request.send();
      
      if (response.statusCode == 200) {
        // Convertir la respuesta a string
        var responseData = await response.stream.bytesToString();
        var decodedResponse = json.decode(responseData);
        
        setState(() {
          _caption = decodedResponse['caption'];
          _isLoading = false;
        });
      } else {
        setState(() {
          _caption = "Error: No se pudo procesar la imagen (${response.statusCode})";
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _caption = "Error de conexión: $e";
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detector de Objetos'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            _image != null
                ? Image.file(
                    _image!,
                    height: 300,
                    width: double.infinity,
                    fit: BoxFit.cover,
                  )
                : Container(
                    height: 300,
                    width: double.infinity,
                    color: Colors.grey[300],
                    child: const Icon(
                      Icons.image,
                      size: 100,
                      color: Colors.grey,
                    ),
                  ),
            const SizedBox(height: 20),
            _isLoading
                ? const CircularProgressIndicator()
                : Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Text(
                      _caption,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: _takePhoto,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Tomar Foto'),
                ),
                const SizedBox(width: 20),
                ElevatedButton.icon(
                  onPressed: _pickImage,
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Galería'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}