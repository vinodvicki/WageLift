import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { api, handleApiError, SalaryFormData } from '../lib/api';

export default function CalculatorScreen() {
  const navigation = useNavigation();
  const [formData, setFormData] = useState<SalaryFormData>({
    annual_salary: 0,
    last_raise_date: '',
    job_title: '',
    company: '',
    location: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const formatSalary = (value: string) => {
    const numericValue = value.replace(/[^0-9]/g, '');
    if (numericValue === '') return '';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(parseInt(numericValue));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.annual_salary || formData.annual_salary < 20000) {
      newErrors.annual_salary = 'Please enter a valid salary (minimum $20,000)';
    }

    if (!formData.last_raise_date) {
      newErrors.last_raise_date = 'Please enter your last raise date';
    } else {
      const raiseDate = new Date(formData.last_raise_date);
      const today = new Date();
      if (raiseDate >= today) {
        newErrors.last_raise_date = 'Date must be in the past';
      }
    }

    if (!formData.job_title.trim()) {
      newErrors.job_title = 'Please enter your job title';
    }

    if (!formData.company.trim()) {
      newErrors.company = 'Please enter your company name';
    }

    if (!formData.location.trim()) {
      newErrors.location = 'Please enter your location';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCalculate = async () => {
    if (!validateForm()) {
      Alert.alert('Validation Error', 'Please fix the errors and try again.');
      return;
    }

    setLoading(true);
    try {
      const cpiData = await api.calculateCPIGap(formData);
      
      // Navigate to results with both form data and calculation results
      navigation.navigate('Results', {
        formData,
        cpiData,
      });
    } catch (error) {
      const errorMessage = handleApiError(error);
      Alert.alert('Calculation Error', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (field: keyof SalaryFormData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView 
        style={styles.scrollView} 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Calculate Your Wage Gap</Text>
          <Text style={styles.subtitle}>
            See how inflation has affected your purchasing power
          </Text>
        </View>

        {/* Form */}
        <View style={styles.formContainer}>
          <Text style={styles.formTitle}>Your Information</Text>

          {/* Current Salary */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Current Annual Salary *</Text>
            <TextInput
              style={[styles.input, errors.annual_salary && styles.inputError]}
              placeholder="$75,000"
              value={formData.annual_salary ? formatSalary(formData.annual_salary.toString()) : ''}
              onChangeText={(text) => {
                const numericValue = text.replace(/[^0-9]/g, '');
                updateFormData('annual_salary', parseInt(numericValue) || 0);
              }}
              keyboardType="numeric"
              placeholderTextColor="#9CA3AF"
            />
            {errors.annual_salary && (
              <Text style={styles.errorText}>{errors.annual_salary}</Text>
            )}
          </View>

          {/* Last Raise Date */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Last Raise Date *</Text>
            <TextInput
              style={[styles.input, errors.last_raise_date && styles.inputError]}
              placeholder="2022-01-01"
              value={formData.last_raise_date}
              onChangeText={(text) => updateFormData('last_raise_date', text)}
              placeholderTextColor="#9CA3AF"
            />
            <Text style={styles.helperText}>Format: YYYY-MM-DD</Text>
            {errors.last_raise_date && (
              <Text style={styles.errorText}>{errors.last_raise_date}</Text>
            )}
          </View>

          {/* Job Title */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Job Title *</Text>
            <TextInput
              style={[styles.input, errors.job_title && styles.inputError]}
              placeholder="Software Engineer"
              value={formData.job_title}
              onChangeText={(text) => updateFormData('job_title', text)}
              placeholderTextColor="#9CA3AF"
            />
            {errors.job_title && (
              <Text style={styles.errorText}>{errors.job_title}</Text>
            )}
          </View>

          {/* Company */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Company *</Text>
            <TextInput
              style={[styles.input, errors.company && styles.inputError]}
              placeholder="Tech Corp"
              value={formData.company}
              onChangeText={(text) => updateFormData('company', text)}
              placeholderTextColor="#9CA3AF"
            />
            {errors.company && (
              <Text style={styles.errorText}>{errors.company}</Text>
            )}
          </View>

          {/* Location */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Location *</Text>
            <TextInput
              style={[styles.input, errors.location && styles.inputError]}
              placeholder="San Francisco, CA"
              value={formData.location}
              onChangeText={(text) => updateFormData('location', text)}
              placeholderTextColor="#9CA3AF"
            />
            {errors.location && (
              <Text style={styles.errorText}>{errors.location}</Text>
            )}
          </View>

          {/* Calculate Button */}
          <TouchableOpacity 
            style={[styles.calculateButton, loading && styles.buttonDisabled]}
            onPress={handleCalculate}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFFFFF" size="small" />
            ) : (
              <>
                <Text style={styles.calculateText}>Calculate My Gap</Text>
                <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
              </>
            )}
          </TouchableOpacity>

          {/* Info Section */}
          <View style={styles.infoSection}>
            <View style={styles.infoRow}>
              <Ionicons name="shield-checkmark" size={20} color="#10b981" />
              <Text style={styles.infoText}>100% Secure</Text>
            </View>
            <View style={styles.infoRow}>
              <Ionicons name="time" size={20} color="#3b82f6" />
              <Text style={styles.infoText}>30 Seconds</Text>
            </View>
            <View style={styles.infoRow}>
              <Ionicons name="gift" size={20} color="#f59e0b" />
              <Text style={styles.infoText}>Free Forever</Text>
            </View>
          </View>
        </View>

        {/* How It Works Preview */}
        <View style={styles.previewSection}>
          <Text style={styles.previewTitle}>What You'll Get</Text>
          <View style={styles.previewItems}>
            <View style={styles.previewItem}>
              <Ionicons name="analytics" size={24} color="#ef4444" />
              <Text style={styles.previewText}>Inflation-adjusted salary calculation</Text>
            </View>
            <View style={styles.previewItem}>
              <Ionicons name="document-text" size={24} color="#3b82f6" />
              <Text style={styles.previewText}>AI-generated raise request letter</Text>
            </View>
            <View style={styles.previewItem}>
              <Ionicons name="trending-up" size={24} color="#10b981" />
              <Text style={styles.previewText}>Market salary insights</Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 40,
  },
  header: {
    backgroundColor: '#3b82f6',
    paddingTop: 20,
    paddingBottom: 40,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.9)',
    textAlign: 'center',
    lineHeight: 22,
  },
  formContainer: {
    backgroundColor: 'white',
    margin: 20,
    padding: 24,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  formTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 24,
    textAlign: 'center',
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    flex: 1,
    fontSize: 18,
    padding: 16,
    color: '#1f2937',
  },
  inputError: {
    borderColor: '#EF4444',
  },
  helperText: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  errorText: {
    fontSize: 12,
    color: '#EF4444',
    marginTop: 4,
  },
  calculateButton: {
    backgroundColor: '#3b82f6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    marginTop: 8,
    shadowColor: '#3b82f6',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonDisabled: {
    backgroundColor: '#9CA3AF',
    shadowOpacity: 0,
    elevation: 0,
  },
  calculateText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
  },
  infoSection: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 24,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  infoRow: {
    alignItems: 'center',
    gap: 4,
  },
  infoText: {
    fontSize: 12,
    color: '#6b7280',
    fontWeight: '500',
  },
  previewSection: {
    marginHorizontal: 20,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  previewTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 16,
  },
  previewItems: {
    gap: 16,
  },
  previewItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  previewText: {
    fontSize: 16,
    color: '#374151',
    flex: 1,
  },
}); 