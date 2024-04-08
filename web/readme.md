# Web version of Phoney Baloney

```
docker-compose build
docker-compose up
```

## Microphone Note

Microphone access requires access via localhost or https. 

I was able to use bore.digital to setup a tunnel to my local machine to do testing with my phone.

```
./bore_darwin_arm64 -ls localhost -lp 8080
```

Safari does not like to share the microphone and will often send 0 byte files instead of audio recordings, I'm not sure why

Android does not have this problem
