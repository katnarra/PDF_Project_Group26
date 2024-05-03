package com.group26.dogfeed

import android.os.StrictMode.ThreadPolicy
import android.os.StrictMode
import android.os.Looper
import android.os.Handler
import java.util.concurrent.Executors
import java.util.Random
import java.net.InetSocketAddress
import android.os.Bundle
import android.os.Build
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import android.app.AlertDialog
import android.app.PendingIntent
import android.app.NotificationManager
import android.app.NotificationChannel
import android.app.Notification
import android.util.Log
import android.content.SharedPreferences
import android.content.Intent
import android.content.Context
import android.widget.EditText
import android.widget.Toast
import java.net.Socket
import java.io.InputStream
import java.io.OutputStream
import java.sql.Date
import com.group26.dogfeed.MainActivity

class MainActivity : AppCompatActivity() {
    companion object {
        lateinit var nm: NotificationManager
        lateinit var notif: Notification
        var ip: String? = ""
    }
    lateinit var sharedPref: SharedPreferences
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        StrictMode.setThreadPolicy(StrictMode.ThreadPolicy.Builder().permitAll().build());
        sharedPref = getPreferences(MODE_PRIVATE)
        MainActivity.notif = NotificationCompat.Builder(
            applicationContext,
            "channelXD"
        )   .setSmallIcon(R.mipmap.ic_launcher_round)
            .setContentTitle("Dog has been successfully fed!") 
            .setChannelId("channelXD")
            .build() 
        MainActivity.nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        var mChannel = NotificationChannel(
            "channelXD",
            "Feeding notification",
            NotificationManager.IMPORTANCE_HIGH
        )
        // among us vibration lol
        mChannel.setVibrationPattern(longArrayOf(
                  10, //       10,
            150, 150, // 100, 200,  
            130, 170, // 100, 200,  
            110, 190, // 100, 200,  
            100, 200, // 100, 200,  
            110, 190, // 100, 200,  
            130, 170, // 100, 200,  
            150, 600, // 100, 650,  
            140,  70, // 100, 110,   
            105, 105, // 100, 110,   
            150, 350, // 100, 400,  
        ))
        MainActivity.nm.createNotificationChannel(mChannel)
        val builder = AlertDialog.Builder(this)
        builder.apply {
            val input = EditText(context)
            val oldIp = sharedPref.getString(getString(R.string.url), "192.168.165.101")
            input.setText(oldIp)
            builder.setView(input)
            setPositiveButton("Connect") { _, _ ->
                MainActivity.ip = input.text.toString()
                with(sharedPref.edit()) {
                    putString(getString(R.string.url), MainActivity.ip)
                    apply()
                }
                ClientClass().run()
            }
        }
        builder.show()
    }
}
class ClientClass() : Thread() {        
    lateinit var inputStream: InputStream
    lateinit var outputStream: OutputStream
    lateinit var socket: Socket
    override fun run() {
        var id = 1
        socket = Socket()
        socket.connect(InetSocketAddress(MainActivity.ip, 8888), 2000)
        inputStream = socket.getInputStream()
        outputStream = socket.getOutputStream()
        val executor = Executors.newSingleThreadExecutor()
        var handler = Handler(Looper.getMainLooper())
        executor.execute(kotlinx.coroutines.Runnable {
            kotlin.run {
                val buffer = ByteArray(1024)
                var byte: Int
                while (true) {
                    byte = inputStream.read(buffer)
                    if (byte > 0) {
                        handler.post(Runnable{
                            kotlin.run {
                                Log.v("Message received, sending notification", "")
                                MainActivity.nm.notify(id, MainActivity.notif)
                                id++
                            }
                        })
                    }
                }
            }
        })
    }
}
