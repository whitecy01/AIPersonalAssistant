package com.aiassistant.AIbackend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class AIController {

    @PostMapping("/process-text")
    public ResponseEntity<String> processText(@RequestBody Map<String, String> request) {
        String userInput = request.get("text");
        System.out.println("📨 받은 텍스트: " + userInput);

        // AI 응답 생성 (임시: 실제 AI 모델 연동 필요)
        String aiResponse = generateAIResponse(userInput);

        System.out.println("🤖 AI 응답: " + aiResponse);
        return ResponseEntity.ok(aiResponse);
    }

    private String generateAIResponse(String userInput) {
        // 실제 AI 모델과 연동할 경우, OpenAI API 또는 자체 AI 모델 연결 필요
        if (userInput.contains("날씨")) {
            return "오늘 서울의 날씨는 맑고 기온은 15도입니다.";
        } else if (userInput.contains("시간")) {
            return "현재 시간은 오후 3시 45분입니다.";
        } else {
            return "죄송합니다. 이해하지 못했습니다.";
        }
    }
}