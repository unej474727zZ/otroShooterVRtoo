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
        public boolean btnAPressed = false;
        public boolean btnXPressed = false;
        public boolean dpadUp = false;
        public boolean dpadDown = false;

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
        public boolean getBtnA() {
            return btnAPressed;
        }

        @JavascriptInterface
        public boolean getBtnX() {
            return btnXPressed;
        }

        @JavascriptInterface
        public boolean getDpadUp() {
            return dpadUp;
        }

        @JavascriptInterface
        public boolean getDpadDown() {
            return dpadDown;
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
                gamepadInterface.r2Pressed = isDown; // Mapear L2 también a correr por si están invertidos
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
                // Ignorado o asignado a otra cosa a futuro
                return super.dispatchKeyEvent(event);
            case KeyEvent.KEYCODE_BUTTON_B:
                // Ignorado o asignado a otra cosa a futuro
                return super.dispatchKeyEvent(event);
            case KeyEvent.KEYCODE_DPAD_UP:
                gamepadInterface.dpadUp = isDown;
                return true;
            case KeyEvent.KEYCODE_DPAD_DOWN:
                gamepadInterface.dpadDown = isDown;
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

            // Leer gatillo derecho R2 como eje con umbral de 0.6f porque el mando descansa en 0.5f
            float axisRTrigger = event.getAxisValue(android.view.MotionEvent.AXIS_RTRIGGER);
            float axisGas = event.getAxisValue(android.view.MotionEvent.AXIS_GAS);
            gamepadInterface.r2AxisPressed = (axisRTrigger > 0.6f || axisGas > 0.6f);
        }
        return super.dispatchGenericMotionEvent(event);
    }
}
