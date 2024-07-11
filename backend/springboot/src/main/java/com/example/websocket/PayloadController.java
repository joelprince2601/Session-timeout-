package com.example.websocket;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
public class PayloadController {

    private static final Logger logger = LoggerFactory.getLogger(PayloadController.class);
    private final JwtUtil jwtUtil;

    @Autowired
    public PayloadController(JwtUtil jwtUtil) {
        this.jwtUtil = jwtUtil;
    }

    @PostMapping("/send-payload")
    public ResponseEntity<String> sendPayload(@RequestBody String payload) {
        try {
            logger.info("Received payload: {}", payload);
            String token = jwtUtil.generateToken(payload);
            logger.info("Generated token: {}", token);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            String requestBody = String.format("{\"payload\":\"%s\",\"token\":\"%s\"}", payload, token);
            HttpEntity<String> request = new HttpEntity<>(requestBody, headers);

            RestTemplate restTemplate = new RestTemplate();
            String fastApiUrl = "http://localhost:8000/receive-payload";
            logger.info("Sending request to FastAPI at: {}", fastApiUrl);
            String response = restTemplate.postForObject(fastApiUrl, request, String.class);
            logger.info("Received response from FastAPI: {}", response);

            return ResponseEntity.ok("Payload sent. Response: " + response);
        } catch (Exception e) {
            logger.error("Error occurred while processing payload", e);
            return ResponseEntity.internalServerError().body("An error occurred: " + e.getMessage());
        }
    }
}
