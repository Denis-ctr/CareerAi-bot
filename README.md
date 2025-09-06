Get free private DeepWikis in Devin
DeepWiki
Denis-ctr/CareerAi-bot


Share

Menu
Overview
Relevant source files
Purpose and Scope
This document provides a high-level introduction to the CareerAI bot system, a Telegram-based career advisory service that leverages artificial intelligence to provide personalized career guidance. The overview covers the system's core purpose, architecture, key components, and user interaction patterns.

For detailed implementation specifics, see Core Implementation. For setup and deployment instructions, see Getting Started. For architectural deep-dive, see System Architecture.

System Overview
CareerAI is an intelligent Telegram bot built in Python that provides personalized career guidance through conversational AI. The system integrates Google's Gemini AI model with a multi-language Telegram interface, storing user preferences and session data in SQLite. The bot supports both Azerbaijani and English languages, offering tailored career roadmaps and skill-based recommendations.

The primary entry point is main.py, which orchestrates all bot functionality including user management, AI integration, and database operations. The system implements an asynchronous architecture using aiogram for Telegram API interactions and aiosqlite for database operations.

Sources: 
README.md
1-83

High-Level System Architecture
System Architecture Overview






















Sources: System architecture diagrams provided in context, 
main.py
1-200
 (inferred from importance score)

Key System Components
Component	Purpose	Implementation
Bot Orchestration	Main application entry point and event loop management	main.py with aiogram.Bot and Dispatcher
User State Management	Track user language preferences and registration status	SQLite database with init_db(), set_user(), get_user() functions
Multi-language Support	Handle Azerbaijani and English interactions	Dynamic prompt construction based on user language preference
AI Integration	Generate personalized career advice	Google Gemini API through google-generativeai library
Message Processing	Handle Telegram message size limits	split_message() function for chunking responses
User Interface	Telegram bot commands and callback handling	start_handler(), lang_handler(), message_handler()
Sources: 
README.md
10-21
 
main.py
1-200
 (inferred from system diagrams)

User Interaction Flow
Bot User Flow

Sources: System flow diagrams provided in context, 
main.py
1-200
 (inferred from handler functions)

Technology Stack
The CareerAI bot system is built on the following technology foundation:

Core Framework
Python: Primary programming language with async/await support
aiogram 3.x: Telegram Bot API framework for handling bot interactions
asyncio: Asynchronous programming support for concurrent operations
AI and External Services
google-generativeai: Google Gemini AI model integration for content generation
Telegram Bot API: Primary user interface and communication channel
Data Persistence
aiosqlite: Asynchronous SQLite database operations
SQLite: User profile and session data storage
Key Features Implementation
Multi-language Support: Dynamic prompt generation for Azerbaijani (lang_az) and English (lang_en)
Message Chunking: Automatic response splitting to handle Telegram's message size limits
State Management: User progression tracking from language selection to active career counseling
Asynchronous Architecture: Non-blocking operations for scalable user handling
Sources: 
README.md
44-52
 dependencies inferred from system architecture diagrams

System Capabilities
The CareerAI bot provides the following core capabilities:

Personalized Career Guidance: AI-generated advice based on user skills, interests, and goals
Career Roadmap Generation: Step-by-step career path planning with actionable recommendations
Multi-language Interaction: Native support for Azerbaijani and English languages
User Session Management: Persistent user profiles and preference storage
Scalable Architecture: Asynchronous design supporting concurrent user interactions
Telegram Integration: Native bot interface with inline keyboards and callback handling
Sources: 
README.md
10-21
 
README.md
26-38