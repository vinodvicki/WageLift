import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { User } from '../lib/api';

const { width, height } = Dimensions.get('window');

interface HomeScreenProps {
  user: User;
}

export default function HomeScreen({ user }: HomeScreenProps) {
  const navigation = useNavigation();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const firstName = user.full_name?.split(' ')[0] || user.email.split('@')[0];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Hero Section */}
      <LinearGradient
        colors={['#667eea', '#764ba2', '#5a67d8']}
        style={styles.heroSection}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.heroContent}>
          {/* Personalized Greeting */}
          <View style={styles.greetingSection}>
            <Text style={styles.greetingText}>
              {getGreeting()}, {firstName}!
            </Text>
            <Text style={styles.greetingSubtext}>
              Ready to reclaim your lost wages?
            </Text>
          </View>

          {/* Trust Badge */}
          <View style={styles.trustBadge}>
            <View style={styles.greenDot} />
            <Text style={styles.trustText}>Used by 500+ professionals</Text>
          </View>

          {/* Hero Title */}
          <Text style={styles.heroTitle}>
            Reclaim Your{'\n'}
            <Text style={styles.highlightText}>Lost Wages</Text>
          </Text>

          {/* Subtitle */}
          <Text style={styles.heroSubtitle}>
            See exactly how inflation cut your pay—and get your raise request ready in 30 seconds.
          </Text>

          {/* CTA Button */}
          <TouchableOpacity
            style={styles.ctaButton}
            onPress={() => navigation.navigate('Calculate' as never)}
          >
            <Ionicons name="calculator" size={24} color="#1a202c" style={styles.buttonIcon} />
            <Text style={styles.ctaText}>Calculate My Gap</Text>
          </TouchableOpacity>

          {/* Trust Icons */}
          <View style={styles.trustIcons}>
            <View style={styles.trustIcon}>
              <Ionicons name="shield" size={20} color="rgba(255,255,255,0.8)" />
              <Text style={styles.trustIconText}>Secure</Text>
            </View>
            <View style={styles.trustIcon}>
              <Ionicons name="flash" size={20} color="rgba(255,255,255,0.8)" />
              <Text style={styles.trustIconText}>Fast</Text>
            </View>
            <View style={styles.trustIcon}>
              <Ionicons name="gift" size={20} color="rgba(255,255,255,0.8)" />
              <Text style={styles.trustIconText}>Free</Text>
            </View>
          </View>
        </View>
      </LinearGradient>

      {/* How It Works Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>How It Works</Text>
        <Text style={styles.sectionSubtitle}>Three simple steps to your raise request</Text>

        <View style={styles.stepsContainer}>
          {/* Step 1 */}
          <View style={styles.step}>
            <View style={[styles.stepIcon, { backgroundColor: '#3b82f6' }]}>
              <Ionicons name="cash" size={32} color="white" />
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>1</Text>
              </View>
            </View>
            <Text style={styles.stepTitle}>Enter Salary</Text>
            <Text style={styles.stepDescription}>
              Input your current salary and when you last received a raise
            </Text>
          </View>

          {/* Step 2 */}
          <View style={styles.step}>
            <View style={[styles.stepIcon, { backgroundColor: '#ef4444' }]}>
              <Ionicons name="trending-down" size={32} color="white" />
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>2</Text>
              </View>
            </View>
            <Text style={styles.stepTitle}>View Gap</Text>
            <Text style={styles.stepDescription}>
              See exactly how much purchasing power inflation has stolen from you
            </Text>
          </View>

          {/* Step 3 */}
          <View style={styles.step}>
            <View style={[styles.stepIcon, { backgroundColor: '#10b981' }]}>
              <Ionicons name="document-text" size={32} color="white" />
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>3</Text>
              </View>
            </View>
            <Text style={styles.stepTitle}>Generate Letter</Text>
            <Text style={styles.stepDescription}>
              Get a professional, data-backed raise request ready to send
            </Text>
          </View>
        </View>
      </View>

      {/* Features Section */}
      <View style={[styles.section, styles.featuresSection]}>
        <Text style={styles.sectionTitle}>Why WageLift Works</Text>
        <Text style={styles.sectionSubtitle}>
          Real data, AI intelligence, and professional presentation combine to give you the strongest possible case
        </Text>

        <View style={styles.featuresContainer}>
          {/* Feature 1 */}
          <View style={styles.featureCard}>
            <View style={[styles.featureIcon, { backgroundColor: '#fee2e2' }]}>
              <Ionicons name="trending-down" size={24} color="#dc2626" />
            </View>
            <Text style={styles.featureTitle}>Real BLS Inflation Data</Text>
            <Text style={styles.featureDescription}>
              Government Consumer Price Index data shows exactly how inflation has eroded your buying power
            </Text>
          </View>

          {/* Feature 2 */}
          <View style={styles.featureCard}>
            <View style={[styles.featureIcon, { backgroundColor: '#dcfce7' }]}>
              <Ionicons name="bar-chart" size={24} color="#16a34a" />
            </View>
            <Text style={styles.featureTitle}>Market Benchmarking</Text>
            <Text style={styles.featureDescription}>
              CareerOneStop API data reveals what others in your role and location actually earn
            </Text>
          </View>

          {/* Feature 3 */}
          <View style={styles.featureCard}>
            <View style={[styles.featureIcon, { backgroundColor: '#dbeafe' }]}>
              <Ionicons name="sparkles" size={24} color="#2563eb" />
            </View>
            <Text style={styles.featureTitle}>AI-Powered Letters</Text>
            <Text style={styles.featureDescription}>
              Professional raise requests written by GPT-4 using your specific data and achievements
            </Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <View style={styles.quickActions}>
          <TouchableOpacity 
            style={styles.quickActionCard}
            onPress={() => navigation.navigate('Calculate' as never)}
          >
            <Ionicons name="calculator" size={32} color="#3b82f6" />
            <Text style={styles.quickActionTitle}>New Calculation</Text>
            <Text style={styles.quickActionSubtitle}>Calculate inflation impact</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.quickActionCard}
            onPress={() => navigation.navigate('Profile' as never)}
          >
            <Ionicons name="analytics" size={32} color="#10b981" />
            <Text style={styles.quickActionTitle}>View History</Text>
            <Text style={styles.quickActionSubtitle}>Past calculations</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  heroSection: {
    paddingTop: 40,
    paddingBottom: 60,
    paddingHorizontal: 20,
    minHeight: height * 0.7,
    justifyContent: 'center',
  },
  heroContent: {
    alignItems: 'center',
  },
  greetingSection: {
    alignItems: 'center',
    marginBottom: 24,
  },
  greetingText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 8,
  },
  greetingSubtext: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.9)',
    textAlign: 'center',
  },
  trustBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginBottom: 24,
  },
  greenDot: {
    width: 8,
    height: 8,
    backgroundColor: '#10b981',
    borderRadius: 4,
    marginRight: 8,
  },
  trustText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
  },
  heroTitle: {
    fontSize: 42,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 50,
  },
  highlightText: {
    color: '#fbbf24',
  },
  heroSubtitle: {
    fontSize: 18,
    color: 'rgba(255,255,255,0.9)',
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 24,
    paddingHorizontal: 20,
  },
  ctaButton: {
    backgroundColor: '#fbbf24',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 32,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonIcon: {
    marginRight: 8,
  },
  ctaText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a202c',
  },
  trustIcons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    maxWidth: 300,
  },
  trustIcon: {
    alignItems: 'center',
  },
  trustIconText: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
    marginTop: 4,
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 40,
  },
  featuresSection: {
    backgroundColor: '#f9fafb',
  },
  sectionTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 22,
  },
  stepsContainer: {
    gap: 32,
  },
  step: {
    alignItems: 'center',
  },
  stepIcon: {
    width: 80,
    height: 80,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    position: 'relative',
  },
  stepNumber: {
    position: 'absolute',
    top: -8,
    right: -8,
    width: 24,
    height: 24,
    backgroundColor: '#fbbf24',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  stepNumberText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#1a202c',
  },
  stepTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  stepDescription: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 20,
    paddingHorizontal: 20,
  },
  featuresContainer: {
    gap: 24,
  },
  featureCard: {
    backgroundColor: 'white',
    padding: 24,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  featureIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  featureDescription: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 20,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  quickActionCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  quickActionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a202c',
    marginTop: 12,
    marginBottom: 4,
    textAlign: 'center',
  },
  quickActionSubtitle: {
    fontSize: 12,
    color: '#718096',
    textAlign: 'center',
  },
}); 