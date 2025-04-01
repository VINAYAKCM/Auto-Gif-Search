import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  VStack,
  Input,
  IconButton,
  Text,
  Flex,
  useDisclosure,
  Icon,
} from '@chakra-ui/react';
import { GifPanel } from './GifPanel';
import { Message } from '../types';
import axios from 'axios';
import { FaGift, FaPaperPlane } from 'react-icons/fa';

interface ChatWindowProps {
  userId: 1 | 2;
  messages: Message[];
  onSendMessage: (message: string, gifUrl?: string) => void;
}

export const ChatWindow = ({ userId, messages, onSendMessage }: ChatWindowProps) => {
  const [inputMessage, setInputMessage] = useState('');
  const [suggestedGifs, setSuggestedGifs] = useState<string[]>([]);
  const [isLoadingGifs, setIsLoadingGifs] = useState(false);
  const { isOpen, onToggle, onClose } = useDisclosure();
  const [lastFetchedText, setLastFetchedText] = useState('');

  // Function to fetch GIF suggestions from the backend
  const fetchGifSuggestions = useCallback(async (text: string) => {
    // Don't fetch if the text is the same as last time
    if (text === lastFetchedText) return;
    
    setIsLoadingGifs(true);
    try {
      console.log('Fetching GIFs for text:', text);
      const response = await axios.post('http://localhost:5001/generate_reply_and_gifs', {
        message: text
      });
      
      console.log('Backend response:', response.data);

      if (response.data.suggested_gifs && response.data.suggested_gifs.length > 0) {
        console.log('Found GIFs:', response.data.suggested_gifs);
        setSuggestedGifs(response.data.suggested_gifs);
        setLastFetchedText(text);
      } else {
        console.log('No GIFs found in response');
        setSuggestedGifs([]);
      }
    } catch (error) {
      console.error('Error fetching GIFs:', error);
      setSuggestedGifs([]);
    } finally {
      setIsLoadingGifs(false);
    }
  }, [lastFetchedText]);

  // Get GIF suggestions when receiving a new message
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.userId !== userId) {
      console.log('New message received, fetching GIFs for:', lastMessage.text);
      fetchGifSuggestions(lastMessage.text);
    }
  }, [messages, userId, fetchGifSuggestions]);

  // Debounce function for input handling
  const debounce = (func: Function, wait: number) => {
    let timeout: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  };

  // Debounced function for getting GIF suggestions while typing
  const debouncedGetSuggestions = debounce((text: string) => {
    if (text.length >= 3) { // Increased minimum length to 3 characters
      console.log('Debounced GIF fetch for:', text);
      fetchGifSuggestions(text);
    }
  }, 1000); // Increased debounce time to 1 second

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const text = e.target.value;
    setInputMessage(text);
    if (isOpen) {
      debouncedGetSuggestions(text);
    }
  };

  const handleSendMessage = (gifUrl?: string) => {
    if (inputMessage.trim() || gifUrl) {
      onSendMessage(inputMessage.trim(), gifUrl);
      setInputMessage('');
      setSuggestedGifs([]); // Clear suggestions after sending
      onClose(); // Close GIF panel after sending
      setLastFetchedText(''); // Reset last fetched text
    }
  };

  return (
    <Box
      w="full"
      h="full"
      borderWidth="1px"
      borderRadius="lg"
      overflow="hidden"
      bg="white"
      color="black"
    >
      <VStack h="full" p={4}>
        <Box flex="1" w="full" overflowY="auto" mb={4}>
          {messages.map((message, index) => (
            <Flex
              key={index}
              justify={message.userId === userId ? 'flex-end' : 'flex-start'}
              mb={2}
            >
              <Box
                maxW="70%"
                bg={message.userId === userId ? 'blue.500' : 'gray.200'}
                color={message.userId === userId ? 'white' : 'black'}
                p={2}
                borderRadius="lg"
              >
                {message.gifUrl ? (
                  <img src={message.gifUrl} alt="GIF" style={{ maxWidth: '100%', borderRadius: '8px' }} />
                ) : (
                  <Text>{message.text}</Text>
                )}
              </Box>
            </Flex>
          ))}
        </Box>

        <Box w="full">
          <Flex mb={2}>
            <IconButton
              aria-label="Toggle GIF panel"
              icon={<Icon as={FaGift} />}
              onClick={onToggle}
              mr={2}
              isLoading={isLoadingGifs}
            />
            <Input
              placeholder="Type a message..."
              value={inputMessage}
              onChange={handleInputChange}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <IconButton
              aria-label="Send message"
              icon={<Icon as={FaPaperPlane} />}
              ml={2}
              onClick={() => handleSendMessage()}
            />
          </Flex>

          {isOpen && (
            <GifPanel
              gifs={suggestedGifs}
              isLoading={isLoadingGifs}
              onGifSelect={(gifUrl: string) => {
                handleSendMessage(gifUrl);
                onClose();
              }}
            />
          )}
        </Box>
      </VStack>
    </Box>
  );
}; 