import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Share,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRoute } from '@react-navigation/native';
import { api, handleApiError, RaiseLetterRequest } from '../lib/api';

interface RouteParams {
  salary: number;
  years: number;
  jobTitle: string;
  inflationLoss: number;
  percentageGap: number;
}

export default function LetterScreen() {
  const route = useRoute();
  const params = route.params as RouteParams;
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [letterContent, setLetterContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [subjectLine, setSubjectLine] = useState('');
  const [keyPoints, setKeyPoints] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [tone, setTone] = useState<'professional' | 'confident' | 'collaborative' | 'assertive'>('professional');

  useEffect(() => {
    generateLetter();
  }, []);

  const generateLetter = async () => {
    setIsGenerating(true);
    setLoading(true);
    try {
      const request: RaiseLetterRequest = {
        user_context: {
          name: 'Your Name', // In a real app, this would come from user profile
          job_title: params.jobTitle,
          company: 'Your Company', // In a real app, this would come from user profile
          years_at_company: params.years,
        },
        cpi_data: {
          dollar_gap: params.inflationLoss,
          percentage_gap: params.percentageGap,
          adjusted_salary: params.salary + params.inflationLoss,
          years_elapsed: params.years,
        },
        tone: tone,
        length: 'standard',
      };

      const response = await api.generateRaiseLetter(request);
      
      setLetterContent(response.letter_content);
      setSubjectLine(response.subject_line);
      setKeyPoints(response.key_points || []);
    } catch (error) {
      const errorMessage = handleApiError(error);
      Alert.alert('Generation Error', errorMessage);
      
      // Fallback to demo content if API fails
      setSubjectLine('Salary Adjustment Request');
      setLetterContent(generateFallbackLetter());
    } finally {
      setIsGenerating(false);
      setLoading(false);
    }
  };

  const generateFallbackLetter = () => {
    const formatCurrency = (amount: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(amount);
    };

    return `Dear [Manager's Name],

I hope this message finds you well. I am writing to request a discussion about adjusting my current salary to reflect the impact of inflation on my purchasing power.

Since my last salary adjustment on ${new Date(Date.now() - params.years * 31536000000).toLocaleDateString()}, inflation has significantly affected the real value of my compensation. Based on official Bureau of Labor Statistics data, my current salary of ${formatCurrency(params.salary)} has the equivalent purchasing power of ${formatCurrency(params.salary - params.inflationLoss)} compared to when it was last set.

Key points for consideration:

• Inflation has reduced my purchasing power by ${params.percentageGap.toFixed(1)}% (${formatCurrency(params.inflationLoss)})
• To maintain the same purchasing power, my salary should be ${formatCurrency(params.salary + params.inflationLoss)}
• This calculation is based on ${params.years} years of official CPI data
• I have continued to deliver strong performance in my role as ${params.jobTitle}

I would appreciate the opportunity to discuss this matter with you and explore how we can address this salary adjustment. I am confident that bringing my compensation in line with current economic conditions will ensure continued mutual success.

Thank you for your time and consideration. I look forward to our discussion.

Best regards,
[Your Name]`;
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    await generateLetter();
    setRegenerating(false);
  };

  const handleShare = async () => {
    try {
      await Share.share({
        message: `Subject: ${subjectLine}\n\n${letterContent}`,
        title: 'Salary Raise Request Letter',
      });
    } catch (error) {
      console.error('Error sharing:', error);
    }
  };

  const handleSave = () => {
    Alert.alert(
      'Letter Saved',
      'Your personalized raise request letter has been saved successfully!',
      [{ text: 'OK' }]
    );
  };

  const handleEmail = () => {
    Alert.alert(
      'Send Email',
      'In a full app, this would open your email client with the letter pre-filled.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Open Email', onPress: () => console.log('Email opened') }
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingTitle}>Generating Your Letter</Text>
        <Text style={styles.loadingSubtitle}>
          Our AI is crafting a personalized raise request based on your data...
        </Text>
        <View style={styles.loadingSteps}>
          <Text style={styles.loadingStep}>✓ Analyzing inflation data</Text>
          <Text style={styles.loadingStep}>✓ Calculating salary adjustment</Text>
          <Text style={styles.loadingStep}>✓ Crafting professional letter</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Your Raise Request</Text>
        <Text style={styles.headerSubtitle}>
          AI-generated letter with your inflation data
        </Text>
      </View>

      {/* Action Bar */}
      <View style={styles.actionBar}>
        <TouchableOpacity
          style={[styles.actionButton, isEditing && styles.activeButton]}
          onPress={() => setIsEditing(!isEditing)}
        >
          <Ionicons 
            name={isEditing ? "checkmark" : "create"} 
            size={20} 
            color={isEditing ? "white" : "#3b82f6"} 
          />
          <Text style={[styles.actionText, isEditing && styles.activeText]}>
            {isEditing ? 'Done' : 'Edit'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.actionButton}
          onPress={handleRegenerate}
          disabled={regenerating}
        >
          {regenerating ? (
            <ActivityIndicator size="small" color="#3B82F6" />
          ) : (
            <Ionicons name="refresh" size={20} color="#3B82F6" />
          )}
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton} onPress={handleShare}>
          <Ionicons name="share" size={20} color="#3b82f6" />
          <Text style={styles.actionText}>Share</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton} onPress={handleSave}>
          <Ionicons name="bookmark" size={20} color="#3b82f6" />
          <Text style={styles.actionText}>Save</Text>
        </TouchableOpacity>
      </View>

      {/* Subject Line */}
      <View style={styles.subjectContainer}>
        <Text style={styles.subjectLabel}>Subject:</Text>
        <TextInput
          style={styles.subjectInput}
          value={subjectLine}
          onChangeText={setSubjectLine}
          editable={isEditing}
          multiline
        />
      </View>

      {/* Letter Content */}
      <ScrollView style={styles.letterContainer} showsVerticalScrollIndicator={false}>
        <View style={styles.letterCard}>
          {isEditing ? (
            <TextInput
              style={styles.letterInput}
              value={letterContent}
              onChangeText={setLetterContent}
              multiline
              textAlignVertical="top"
              placeholder="Edit your letter content..."
            />
          ) : (
            <Text style={styles.letterText}>{letterContent}</Text>
          )}
        </View>

        {/* Key Points */}
        {keyPoints.length > 0 && (
          <View style={styles.keyPointsContainer}>
            <Text style={styles.keyPointsTitle}>Key Points Covered:</Text>
            {keyPoints.map((point, index) => (
              <View key={index} style={styles.keyPointItem}>
                <Ionicons name="checkmark-circle" size={16} color="#10B981" />
                <Text style={styles.keyPointText}>{point}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Bottom Actions */}
      <View style={styles.bottomActions}>
        <TouchableOpacity style={styles.primaryButton} onPress={handleEmail}>
          <Ionicons name="mail" size={20} color="white" />
          <Text style={styles.primaryButtonText}>Send Email</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
    padding: 20,
  },
  loadingTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
    marginBottom: 8,
  },
  loadingSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 30,
  },
  loadingSteps: {
    alignItems: 'flex-start',
    gap: 8,
  },
  loadingStep: {
    fontSize: 14,
    color: '#10b981',
    marginBottom: 8,
  },
  header: {
    backgroundColor: '#3b82f6',
    paddingTop: 20,
    paddingBottom: 24,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.9)',
    textAlign: 'center',
  },
  actionBar: {
    flexDirection: 'row',
    backgroundColor: 'white',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
    gap: 16,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    gap: 6,
  },
  activeButton: {
    backgroundColor: '#3b82f6',
    borderColor: '#3b82f6',
  },
  actionText: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '500',
  },
  activeText: {
    color: 'white',
  },
  letterContainer: {
    flex: 1,
    padding: 20,
  },
  letterCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  letterText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#1f2937',
  },
  letterInput: {
    fontSize: 16,
    lineHeight: 24,
    color: '#1f2937',
    minHeight: 400,
    textAlignVertical: 'top',
  },
  subjectContainer: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  subjectLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  subjectInput: {
    fontSize: 16,
    color: '#111827',
    fontWeight: '500',
  },
  keyPointsContainer: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 20,
    borderRadius: 8,
  },
  keyPointsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  keyPointItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  keyPointText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 8,
    flex: 1,
    lineHeight: 20,
  },
  bottomActions: {
    flexDirection: 'row',
    padding: 20,
    gap: 12,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  primaryButton: {
    flex: 1,
    backgroundColor: '#3b82f6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 8,
  },
  primaryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
}); 