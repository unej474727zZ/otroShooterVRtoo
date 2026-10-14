package com.ildem.otroshootervr;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.JavascriptInterface;
import androidx.webkit.WebViewAssetLoader;

public class MainActivity extends Activity {
    private WebView webView;

    public class GamepadInterface {
        public float rightX = 0;
        public float rightY = 0;
        public boolean r1Pressed = false;
        public boolean r2Pressed = false;
        public boolean r2AxisPressed = false;
        public boolean l1Pressed = false;
        public boolean l2Pressed = false;
        public boolean l2AxisPressed = false;
        public boolean btnAPressed = false;
        public boolean btnXPressed = false;
        public boolean btnYPressed = false;
        public boolean btnBPressed = false;
        public boolean btnSelectPressed = false;
        public boolean btnStartPressed = false;
        public boolean dpadUp = false;
        public boolean dpadDown = false;
        public boolean dpadLeft = false;
        public boolean dpadRight = false;
        public boolean dpadHatUp = false;
        public boolean dpadHatDown = false;
        public boolean dpadHatLeft = false;
        public boolean dpadHatRight = false;

        @JavascriptInterface
        public float getRightX() {
            return rightX;
        }

        @JavascriptInterface
        public float getRightY() {
            return rightY;
        }

        @JavascriptInterface
        public boolean getR1() {
            return r1Pressed;
        }

        @JavascriptInterface
        public boolean getR2() {
            return r2Pressed || r2AxisPressed;
        }

        @JavascriptInterface
        public boolean getL1() {
            return l1Pressed;
        }

        @JavascriptInterface
        public boolean getL2() {
            return l2Pressed || l2AxisPressed;
        }

        @JavascriptInterface
        public boolean getBtnA() {
            return btnAPressed;
        }

        @JavascriptInterface
        public boolean getBtnX() {
            return btnXPressed;
        }

        @JavascriptInterface
        public boolean getBtnY() {
            return btnYPressed;
        }

        @JavascriptInterface
        public boolean getBtnB() {
            return btnBPressed;
        }

        @JavascriptInterface
        public boolean getBtnSelect() {
            return btnSelectPressed;
        }

        @JavascriptInterface
        public boolean getBtnStart() {
            return btnStartPressed;
        }

        @JavascriptInterface
        public boolean getDpadUp() {
            return dpadUp || dpadHatUp;
        }

        @JavascriptInterface
        public boolean getDpadDown() {
            return dpadDown || dpadHatDown;
        }

        @JavascriptInterface
        public boolean getDpadLeft() {
            return dpadLeft || dpadHatLeft;
        }

        @JavascriptInterface
        public boolean getDpadRight() {
            return dpadRight || dpadHatRight;
        }

        @JavascriptInterface
        public void sendLogToPc(String jsonLogs) {
            new Thread(() -> {
                try {
                    java.net.URL url = new java.net.URL("http://192.168.1.103:8080/log");
                    java.net.HttpURLConnection conn = (java.net.HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("POST");
                    conn.setRequestProperty("Content-Type", "application/json; utf-8");
                    conn.setDoOutput(true);
                    conn.setConnectTimeout(3000);
                    conn.setReadTimeout(3000);
                    try (java.io.OutputStream os = conn.getOutputStream()) {
                        byte[] input = jsonLogs.getBytes("utf-8");
                        os.write(input, 0, input.length);
                    }
                    int code = conn.getResponseCode();
                    android.util.Log.d("VR_LOG", "Log enviado a PC con codigo: " + code);
                } catch (Exception e) {
                    android.util.Log.e("VR_LOG", "Error enviando log a PC", e);
                }
            }).start();
        }
    }

    private GamepadInterface gamepadInterface = new GamepadInterface();

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Poner la aplicación en Pantalla Completa Inmersiva
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                        | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_FULLSCREEN);

        // Creamos el WebView que cargará el juego
        webView = new WebView(this);
        setContentView(webView);

        // Configuraciones vitales para juegos WebGL/WebXR en Android
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);

        // Esto permite la aceleración gráfica de WebGL
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);

        // Clientes web para manejar las alertas y la navegación interna
        webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(gamepadInterface, "AndroidGamepad");

        final WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return assetLoader.shouldInterceptRequest(request.getUrl());
            }
        });

        // Cargamos nuestro archivo index.html a través del AssetLoader seguro
        webView.loadUrl("https://appassets.androidplatform.net/assets/index.html");
    }

    // Para mantener la pantalla completa si el usuario sale y vuelve a entrar a la
    // app
    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            getWindow().getDecorView().setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                            | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                            | View.SYSTEM_UI_FLAG_FULLSCREEN);
        }
    }

    // Para que los botones del Gamepad lleguen al WebView de forma 100% segura
    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        boolean isDown = (event.getAction() == KeyEvent.ACTION_DOWN);
        int keyCode = event.getKeyCode();

        switch (keyCode) {
            case KeyEvent.KEYCODE_BUTTON_R1:
                gamepadInterface.r1Pressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BUTTON_R2:
                gamepadInterface.r2Pressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BUTTON_L2:
                gamepadInterface.l2Pressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BUTTON_L1:
                gamepadInterface.l1Pressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BUTTON_A:
                gamepadInterface.btnAPressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BUTTON_X:
                gamepadInterface.btnXPressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BUTTON_Y:
                gamepadInterface.btnYPressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BUTTON_B:
                gamepadInterface.btnBPressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BUTTON_SELECT:
                gamepadInterface.btnSelectPressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BUTTON_START:
            case KeyEvent.KEYCODE_MENU:
            case KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE:
                gamepadInterface.btnStartPressed = isDown;
                return true;
            case KeyEvent.KEYCODE_BACK:
                // Si viene del mando (muchos mandos chinos envían BACK en vez de SELECT)
                if ((event.getSource() & android.view.InputDevice.SOURCE_GAMEPAD) == android.view.InputDevice.SOURCE_GAMEPAD
                        || (event.getSource() & android.view.InputDevice.SOURCE_JOYSTICK) == android.view.InputDevice.SOURCE_JOYSTICK) {
                    gamepadInterface.btnSelectPressed = isDown;
                    return true;
                }
                break;
            case KeyEvent.KEYCODE_DPAD_UP:
                gamepadInterface.dpadUp = isDown;
                return true;
            case KeyEvent.KEYCODE_DPAD_DOWN:
                gamepadInterface.dpadDown = isDown;
                return true;
            case KeyEvent.KEYCODE_DPAD_LEFT:
                gamepadInterface.dpadLeft = isDown;
                return true;
            case KeyEvent.KEYCODE_DPAD_RIGHT:
                gamepadInterface.dpadRight = isDown;
                return true;
        }

        return super.dispatchKeyEvent(event);
    }

    // PUENTE NATIVO: El navegador WebView a veces recorta los ejes del gamepad
    // (borra el eje 4 y 5 de la palanca derecha).
    // Con esto leemos la palanca derecha DIRECTAMENTE desde el sistema Android y se
    // la pasamos al juego.
    @Override
    public boolean dispatchGenericMotionEvent(android.view.MotionEvent event) {
        if ((event.getSource() & android.view.InputDevice.SOURCE_JOYSTICK) == android.view.InputDevice.SOURCE_JOYSTICK
                && event.getAction() == android.view.MotionEvent.ACTION_MOVE) {

            // Leer todos los ejes posibles que usan los controles chinos para la palanca
            // derecha
            float axisZ = event.getAxisValue(android.view.MotionEvent.AXIS_Z); // Eje 11
            float axisRZ = event.getAxisValue(android.view.MotionEvent.AXIS_RZ); // Eje 14
            float axisRX = event.getAxisValue(android.view.MotionEvent.AXIS_RX); // Eje 12
            float axisRY = event.getAxisValue(android.view.MotionEvent.AXIS_RY); // Eje 13

            float rightX = 0;
            float rightY = 0;
            if (Math.abs(axisZ) > 0.1 || Math.abs(axisRZ) > 0.1) {
                rightX = axisZ;
                rightY = axisRZ;
            } else if (Math.abs(axisRX) > 0.1 || Math.abs(axisRY) > 0.1) {
                rightX = axisRX;
                rightY = axisRY;
            }

            gamepadInterface.rightX = rightX;
            gamepadInterface.rightY = rightY;

            // Leer D-Pad / Cruz analógica (HAT X / HAT Y)
            float hatX = event.getAxisValue(android.view.MotionEvent.AXIS_HAT_X);
            float hatY = event.getAxisValue(android.view.MotionEvent.AXIS_HAT_Y);
            gamepadInterface.dpadHatUp = (hatY < -0.5f);
            gamepadInterface.dpadHatDown = (hatY > 0.5f);
            gamepadInterface.dpadHatLeft = (hatX < -0.5f);
            gamepadInterface.dpadHatRight = (hatX > 0.5f);

            // GATILLOS ANALÓGICOS:
            // OJO: En mandos Bluetooth, al girar la palanca a la derecha (axisZ > 0), Android también reporta AXIS_BRAKE.
            // Al girar la palanca abajo (axisRZ > 0), Android también reporta AXIS_GAS.
            // Para que NO se confunda girar la cámara con presionar L2 o R2:
            // 1) Si se mueve la palanca derecha, ignoramos AXIS_BRAKE y AXIS_GAS.
            // 2) Solo si la palanca derecha está en reposo aceptamos AXIS_BRAKE como L2 o AXIS_GAS como R2.
            boolean isRightStickDeflected = (Math.abs(rightX) > 0.15f || Math.abs(rightY) > 0.15f);

            float axisLTrigger = event.getAxisValue(android.view.MotionEvent.AXIS_LTRIGGER);
            float axisBrake = event.getAxisValue(android.view.MotionEvent.AXIS_BRAKE);
            if (axisLTrigger > 0.75f) {
                gamepadInterface.l2AxisPressed = true;
            } else if (!isRightStickDeflected && axisBrake > 0.75f) {
                gamepadInterface.l2AxisPressed = true;
            } else if (axisLTrigger < 0.3f && axisBrake < 0.3f) {
                gamepadInterface.l2AxisPressed = false;
            }

            float axisRTrigger = event.getAxisValue(android.view.MotionEvent.AXIS_RTRIGGER);
            float axisGas = event.getAxisValue(android.view.MotionEvent.AXIS_GAS);
            if (axisRTrigger > 0.75f) {
                gamepadInterface.r2AxisPressed = true;
            } else if (!isRightStickDeflected && axisGas > 0.75f) {
                gamepadInterface.r2AxisPressed = true;
            } else if (axisRTrigger < 0.3f && axisGas < 0.3f) {
                gamepadInterface.r2AxisPressed = false;
            }
        }
        return super.dispatchGenericMotionEvent(event);
    }
}
