plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    namespace = "com.group26.dogfeed"
    compileSdk = 34
    defaultConfig {
        minSdk = 34
        targetSdk = 34
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("com.google.android.material:material:+")
}
