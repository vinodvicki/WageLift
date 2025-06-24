import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');

interface RouteParams {
  salary: number;
  years: number;
  jobTitle: string;
}

export default function ResultsScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const params = route.params as RouteParams;
  
  const [animatedValue] = useState(new Animated.Value(0));
  const [results, setResults] = useState({
    inflationLoss: 0,
    adjustedSalary: 0,
    percentageGap: 0,
    raiseNeeded: 0,
    annualInflationRate: 5.8,
  });

  useEffect(() => {
    if (params) {
      calculateResults();
      animateResults();
    }
  }, [params]);

  const calculateResults = () => {
    const { salary, years } = params;
    const annualInflationRate = 5.8;
    const totalInflation = Math.pow(1 + annualInflationRate / 100, years) - 1;
    const adjustedSalary = salary * (1 + totalInflation);
    const inflationLoss = adjustedSalary - salary;
    const percentageGap = (inflationLoss / salary) * 100;

    setResults({
      inflationLoss,
      adjustedSalary,
      percentageGap,
      raiseNeeded: percentageGap,
      annualInflationRate,
    });
  };

  const animateResults = () => {
    Animated.timing(animatedValue, {
      toValue: 1,
      duration: 1000,
      useNativeDriver: false,
    }).start();
  };

  const handleGenerateLetter = () => {
    navigation.navigate('Letter' as never, {
      ...params,
      ...results,
    } as never);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (!params) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="warning" size={48} color="#f59e0b" />
        <Text style={styles.errorText}>No calculation data found</Text>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Main Result Card */}
      <View style={styles.mainResultCard}>
        <LinearGradient
          colors={['#fee2e2', '#fecaca']}
          style={styles.lossGradient}
        >
          <Text style={styles.lossAmount}>
            {formatCurrency(results.inflationLoss)}
          </Text>
          <Text style={styles.lossLabel}>
            Lost to inflation over {params.years} year{params.years !== 1 ? 's' : ''}
          </Text>
          
          {/* Animated Progress Bar */}
          <View style={styles.progressContainer}>
            <Animated.View
              style={[
                styles.progressBar,
                {
                  width: animatedValue.interpolate({
                    inputRange: [0, 1],
                    outputRange: ['0%', `${Math.min(results.percentageGap * 5, 100)}%`],
                  }),
                },
              ]}
            />
          </View>
          
          <Text style={styles.raiseNeeded}>
            {results.raiseNeeded.toFixed(1)}% raise needed to break even
          </Text>
        </LinearGradient>
      </View>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <View style={[styles.statCard, styles.inflationCard]}>
          <Ionicons name="trending-up" size={24} color="#3b82f6" />
          <Text style={styles.statValue}>
            {formatCurrency(results.adjustedSalary)}
          </Text>
          <Text style={styles.statLabel}>Inflation-adjusted salary</Text>
        </View>

        <View style={[styles.statCard, styles.rateCard]}>
          <Ionicons name="analytics" size={24} color="#8b5cf6" />
          <Text style={styles.statValue}>
            {results.annualInflationRate}%
          </Text>
          <Text style={styles.statLabel}>Annual inflation rate</Text>
        </View>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionContainer}>
        <TouchableOpacity style={styles.primaryButton} onPress={handleGenerateLetter}>
          <Ionicons name="document-text" size={20} color="white" />
          <Text style={styles.primaryButtonText}>Generate Raise Letter</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.secondaryButton}>
          <Ionicons name="share" size={20} color="#3b82f6" />
          <Text style={styles.secondaryButtonText}>Share Results</Text>
        </TouchableOpacity>
      </View>

      {/* Insights Section */}
      <View style={styles.insightsSection}>
        <Text style={styles.insightsTitle}>Your Insights</Text>
        
        <View style={styles.insightCard}>
          <View style={styles.insightIcon}>
            <Ionicons name="trending-down" size={20} color="#dc2626" />
          </View>
          <View style={styles.insightContent}>
            <Text style={styles.insightTitle}>Purchasing Power Loss</Text>
            <Text style={styles.insightText}>
              Your {formatCurrency(params.salary)} salary from {params.years} years ago 
              would need to be {formatCurrency(results.adjustedSalary)} today to maintain 
              the same purchasing power.
            </Text>
          </View>
        </View>

        <View style={styles.insightCard}>
          <View style={styles.insightIcon}>
            <Ionicons name="briefcase" size={20} color="#3b82f6" />
          </View>
          <View style={styles.insightContent}>
            <Text style={styles.insightTitle}>Market Position</Text>
            <Text style={styles.insightText}>
              As a {params.jobTitle}, you're experiencing the same inflation impact 
              as millions of other professionals. Data-driven raise requests have 
              a 73% higher success rate.
            </Text>
          </View>
        </View>

        <View style={styles.insightCard}>
          <View style={styles.insightIcon}>
            <Ionicons name="bulb" size={20} color="#f59e0b" />
          </View>
          <View style={styles.insightContent}>
            <Text style={styles.insightTitle}>Next Steps</Text>
            <Text style={styles.insightText}>
              Generate your personalized raise letter with AI-powered content 
              that includes your specific inflation data and market benchmarks.
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 18,
    color: '#6b7280',
    marginTop: 16,
    marginBottom: 24,
  },
  backButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  backButtonText: {
    color: 'white',
    fontWeight: '600',
  },
  mainResultCard: {
    margin: 20,
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  lossGradient: {
    padding: 32,
    alignItems: 'center',
  },
  lossAmount: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#dc2626',
    marginBottom: 8,
  },
  lossLabel: {
    fontSize: 16,
    color: '#7f1d1d',
    textAlign: 'center',
    marginBottom: 24,
  },
  progressContainer: {
    width: '100%',
    height: 8,
    backgroundColor: '#fca5a5',
    borderRadius: 4,
    marginBottom: 16,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#dc2626',
    borderRadius: 4,
  },
  raiseNeeded: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#059669',
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    marginHorizontal: 20,
    gap: 12,
  },
  statCard: {
    flex: 1,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  inflationCard: {
    backgroundColor: '#eff6ff',
    borderColor: '#bfdbfe',
    borderWidth: 1,
  },
  rateCard: {
    backgroundColor: '#f3e8ff',
    borderColor: '#c4b5fd',
    borderWidth: 1,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
  actionContainer: {
    margin: 20,
    gap: 12,
  },
  primaryButton: {
    backgroundColor: '#3b82f6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 8,
    shadowColor: '#3b82f6',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  primaryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: 'white',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#3b82f6',
    gap: 8,
  },
  secondaryButtonText: {
    color: '#3b82f6',
    fontSize: 16,
    fontWeight: '600',
  },
  insightsSection: {
    margin: 20,
  },
  insightsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
  },
  insightCard: {
    backgroundColor: 'white',
    flexDirection: 'row',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  insightIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  insightContent: {
    flex: 1,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  insightText: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
}); 