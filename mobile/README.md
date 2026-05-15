# Mobile Release Instructions

To build the mobile app for release:

1. Update the API endpoint in your code to point to the Render backend:
   `https://boq-ai-backend-service.onrender.com`

2. Run the flutter build command:
   `flutter build apk --release` or `flutter build ios --release`

3. Ensure permissions for internet access are added to AndroidManifest.xml and Info.plist.
