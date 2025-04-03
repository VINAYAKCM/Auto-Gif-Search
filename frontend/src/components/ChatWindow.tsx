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
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
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
  const [replyGifs, setReplyGifs] = useState<string[]>([]);
  const [isLoadingGifs, setIsLoadingGifs] = useState(false);
  const [isLoadingReplyGifs, setIsLoadingReplyGifs] = useState(false);
  const { isOpen, onToggle, onClose } = useDisclosure();
  const [lastFetchedText, setLastFetchedText] = useState('');
  const [lastFetchedReply, setLastFetchedReply] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  // Function to fetch text-based GIF suggestions
  const fetchTextGifs = useCallback(async (text: string) => {
    if (text === lastFetchedText) return;
    
    setIsLoadingGifs(true);
    try {
      console.log('Fetching text GIFs for:', text);
      const response = await axios.post('http://localhost:5001/generate_text_gifs', {
        message: text
      });
      
      if (response.data.suggested_gifs && response.data.suggested_gifs.length > 0) {
        console.log('Found text GIFs:', response.data.suggested_gifs);
        setSuggestedGifs(response.data.suggested_gifs);
        setLastFetchedText(text);
      } else {
        console.log('No text GIFs found');
        setSuggestedGifs([]);
      }
    } catch (error) {
      console.error('Error fetching text GIFs:', error);
      setSuggestedGifs([]);
    } finally {
      setIsLoadingGifs(false);
    }
  }, [lastFetchedText]);

  // Function to fetch reply GIF suggestions
  const fetchReplyGifs = useCallback(async (text: string) => {
    if (text === lastFetchedReply) return;
    
    setIsLoadingReplyGifs(true);
    try {
      console.log('Fetching reply GIFs for:', text);
      const response = await axios.post('http://localhost:5001/generate_reply_gifs', {
        message: text
      });
      
      if (response.data.suggested_gifs && response.data.suggested_gifs.length > 0) {
        console.log('Found reply GIFs:', response.data.suggested_gifs);
        setReplyGifs(response.data.suggested_gifs);
        setLastFetchedReply(text);
      } else {
        console.log('No reply GIFs found');
        setReplyGifs([]);
      }
    } catch (error) {
      console.error('Error fetching reply GIFs:', error);
      setReplyGifs([]);
    } finally {
      setIsLoadingReplyGifs(false);
    }
  }, [lastFetchedReply]);

  // Get GIF suggestions when receiving a new message
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.userId !== userId) {
      console.log('New message received, fetching reply GIFs for:', lastMessage.text);
      fetchReplyGifs(lastMessage.text);
      setActiveTab(0); // Switch to reply GIFs tab
    }
  }, [messages, userId, fetchReplyGifs]);

  // Debounce function for input handling
  const debounce = (func: Function, wait: number) => {
    let timeout: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  };

  // Debounced function for getting text GIF suggestions while typing
  const debouncedGetTextGifs = debounce((text: string) => {
    if (text.length >= 3) {
      console.log('Debounced text GIF fetch for:', text);
      fetchTextGifs(text);
      setActiveTab(1); // Switch to text GIFs tab
    } else {
      setSuggestedGifs([]); // Clear suggestions if text is too short
    }
  }, 1000);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const text = e.target.value;
    setInputMessage(text);
    if (isOpen) {
      debouncedGetTextGifs(text);
    }
  };

  const handleSendMessage = (gifUrl?: string) => {
    if (inputMessage.trim() || gifUrl) {
      onSendMessage(inputMessage.trim(), gifUrl);
      setInputMessage('');
      setSuggestedGifs([]);
      setReplyGifs([]);
      onClose();
      setLastFetchedText('');
      setLastFetchedReply('');
    }
  };

  const handleGifPanelToggle = () => {
    if (!isOpen) {
      // When opening the panel
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.userId !== userId) {
        // If there's a message to reply to, show reply GIFs
        fetchReplyGifs(lastMessage.text);
        setActiveTab(0);
      } else if (inputMessage.length >= 3) {
        // If there's text in the input, show text GIFs
        fetchTextGifs(inputMessage);
        setActiveTab(1);
      }
    }
    onToggle();
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
              onClick={handleGifPanelToggle}
              mr={2}
              isLoading={isLoadingGifs || isLoadingReplyGifs}
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
            <Box>
              <Tabs index={activeTab} onChange={setActiveTab}>
                <TabList>
                  <Tab>Reply GIFs</Tab>
                  <Tab>Text GIFs</Tab>
                  <Tab>Search</Tab>
                </TabList>
                <TabPanels>
                  <TabPanel>
                    <GifPanel
                      gifs={replyGifs}
                      isLoading={isLoadingReplyGifs}
                      onGifSelect={(gifUrl: string) => {
                        handleSendMessage(gifUrl);
                        onClose();
                      }}
                    />
                  </TabPanel>
                  <TabPanel>
                    <GifPanel
                      gifs={suggestedGifs}
                      isLoading={isLoadingGifs}
                      onGifSelect={(gifUrl: string) => {
                        handleSendMessage(gifUrl);
                        onClose();
                      }}
                    />
                  </TabPanel>
                  <TabPanel>
                    <GifPanel
                      mode="search"
                      onGifSelect={(gifUrl: string) => {
                        handleSendMessage(gifUrl);
                        onClose();
                      }}
                    />
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </Box>
          )}
        </Box>
      </VStack>
    </Box>
  );
}; 