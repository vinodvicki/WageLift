import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { User } from '../lib/api';

interface ProfileScreenProps {
  user: User;
  onSignOut: () => void;
}

export default function ProfileScreen({ user, onSignOut }: ProfileScreenProps) {
  const handleSignOut = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Sign Out', style: 'destructive', onPress: onSignOut },
      ]
    );
  };

  const handleSupport = () => {
    Alert.alert(
      'Support',
      'Contact our support team at support@wagelift.com',
      [{ text: 'OK' }]
    );
  };

  const MenuSection = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <View style={styles.menuSection}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );

  const MenuItem = ({ 
    icon, 
    title, 
    subtitle, 
    onPress, 
    showArrow = true,
    color = '#374151'
  }: {
    icon: string;
    title: string;
    subtitle?: string;
    onPress: () => void;
    showArrow?: boolean;
    color?: string;
  }) => (
    <TouchableOpacity style={styles.menuItem} onPress={onPress}>
      <View style={styles.menuItemLeft}>
        <View style={[styles.menuIcon, { backgroundColor: `${color}15` }]}>
          <Ionicons name={icon as any} size={20} color={color} />
        </View>
        <View style={styles.menuText}>
          <Text style={[styles.menuTitle, { color }]}>{title}</Text>
          {subtitle && <Text style={styles.menuSubtitle}>{subtitle}</Text>}
        </View>
      </View>
      {showArrow && (
        <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
      )}
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* User Info */}
      <View style={styles.userSection}>
        <View style={styles.avatar}>
          <Ionicons name="person" size={32} color="white" />
        </View>
        <Text style={styles.userName}>{user.full_name || 'Professional User'}</Text>
        <Text style={styles.userEmail}>{user.email}</Text>
      </View>

      {/* Calculation History */}
      <MenuSection title="Recent Activity">
        <MenuItem
          icon="calculator"
          title="Recent Calculations"
          subtitle="View your inflation impact calculations"
          onPress={() => console.log('View calculations')}
        />
        <MenuItem
          icon="document-text"
          title="Generated Letters"
          subtitle="Manage your raise request letters"
          onPress={() => console.log('View letters')}
        />
      </MenuSection>

      {/* Account Settings */}
      <MenuSection title="Account">
        <MenuItem
          icon="person-circle"
          title="Personal Information"
          subtitle="Update your profile details"
          onPress={() => console.log('Edit profile')}
        />
        <MenuItem
          icon="notifications"
          title="Notifications"
          subtitle="Manage your notification preferences"
          onPress={() => console.log('Notifications')}
        />
        <MenuItem
          icon="shield-checkmark"
          title="Privacy & Security"
          subtitle="Control your data and security settings"
          onPress={() => console.log('Privacy')}
        />
      </MenuSection>

      {/* App Settings */}
      <MenuSection title="App">
        <MenuItem
          icon="document-text"
          title="Saved Letters"
          subtitle="View and manage your raise letters"
          onPress={() => console.log('Saved letters')}
        />
        <MenuItem
          icon="analytics"
          title="Calculation History"
          subtitle="Review your past calculations"
          onPress={() => console.log('History')}
        />
        <MenuItem
          icon="download"
          title="Export Data"
          subtitle="Download your data"
          onPress={() => console.log('Export')}
        />
      </MenuSection>

      {/* Support */}
      <MenuSection title="Support">
        <MenuItem
          icon="help-circle"
          title="Help Center"
          subtitle="Get answers to common questions"
          onPress={handleSupport}
        />
        <MenuItem
          icon="chatbubble"
          title="Contact Support"
          subtitle="Get in touch with our team"
          onPress={handleSupport}
        />
        <MenuItem
          icon="star"
          title="Rate WageLift"
          subtitle="Share your experience"
          onPress={() => console.log('Rate app')}
        />
      </MenuSection>

      {/* About */}
      <MenuSection title="About">
        <MenuItem
          icon="information-circle"
          title="About WageLift"
          subtitle="Learn more about our mission"
          onPress={() => console.log('About')}
        />
        <MenuItem
          icon="document"
          title="Terms of Service"
          onPress={() => console.log('Terms')}
        />
        <MenuItem
          icon="shield"
          title="Privacy Policy"
          onPress={() => console.log('Privacy policy')}
        />
        <MenuItem
          icon="code"
          title="Version"
          subtitle="1.0.0 (Build 1)"
          onPress={() => console.log('Version')}
          showArrow={false}
        />
      </MenuSection>

      {/* Sign Out */}
      <View style={styles.signOutSection}>
        <TouchableOpacity style={styles.signOutButton} onPress={handleSignOut}>
          <Ionicons name="log-out" size={20} color="#dc2626" />
          <Text style={styles.signOutText}>Sign Out</Text>
        </TouchableOpacity>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          WageLift helps you quantify purchasing power loss due to inflation
        </Text>
        <Text style={styles.footerText}>
          © 2024 WageLift. All rights reserved.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  userSection: {
    backgroundColor: '#fff',
    padding: 24,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#3b82f6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: '#6b7280',
  },
  menuSection: {
    backgroundColor: '#fff',
    marginTop: 16,
    paddingVertical: 8,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  menuIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  menuText: {
    flex: 1,
  },
  menuTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#374151',
  },
  menuSubtitle: {
    fontSize: 13,
    color: '#6b7280',
    marginTop: 2,
  },
  signOutSection: {
    backgroundColor: '#fff',
    marginTop: 16,
    marginBottom: 32,
  },
  signOutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
  },
  signOutText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#dc2626',
    marginLeft: 8,
  },
  footer: {
    padding: 24,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#9ca3af',
    textAlign: 'center',
    lineHeight: 18,
    marginBottom: 4,
  },
}); 