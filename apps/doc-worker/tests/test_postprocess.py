"""Unit tests for postprocess."""
import pytest
from src.pipeline.postprocess import (
    normalize_date,
    normalize_cpf,
    normalize_crm,
    normalize_phone,
    clean_text
)


class TestNormalizeDate:
    """Tests for normalize_date function."""
    
    def test_normalize_date_should_handle_dd_mm_yyyy_format(self):
        """Test that normalize_date handles DD/MM/YYYY format."""
        # Act
        result = normalize_date("15/03/2024")
        
        # Assert
        assert result == "15/03/2024"
    
    def test_normalize_date_should_handle_dd_mm_yy_format(self):
        """Test that normalize_date handles DD/MM/YY format."""
        # Act
        result = normalize_date("15/03/24")
        
        # Assert
        assert result == "15/03/2024"
    
    def test_normalize_date_should_handle_dash_separator(self):
        """Test that normalize_date handles dash separator."""
        # Act
        result = normalize_date("15-03-2024")
        
        # Assert
        assert result == "15/03/2024"
    
    def test_normalize_date_should_return_none_for_invalid_format(self):
        """Test that normalize_date returns None for invalid format."""
        # Act
        result = normalize_date("invalid date")
        
        # Assert
        assert result is None
    
    def test_normalize_date_should_return_none_for_empty_string(self):
        """Test that normalize_date returns None for empty string."""
        # Act
        result = normalize_date("")
        
        # Assert
        assert result is None


class TestNormalizeCpf:
    """Tests for normalize_cpf function."""
    
    def test_normalize_cpf_should_format_with_dots_and_dash(self):
        """Test that normalize_cpf formats CPF with dots and dash."""
        # Act
        result = normalize_cpf("12345678901")
        
        # Assert
        assert result == "123.456.789-01"
    
    def test_normalize_cpf_should_handle_already_formatted(self):
        """Test that normalize_cpf handles already formatted CPF."""
        # Act
        result = normalize_cpf("123.456.789-01")
        
        # Assert
        assert result == "123.456.789-01"
    
    def test_normalize_cpf_should_handle_with_spaces(self):
        """Test that normalize_cpf handles CPF with spaces."""
        # Act
        result = normalize_cpf("123 456 789 01")
        
        # Assert
        assert result == "123.456.789-01"
    
    def test_normalize_cpf_should_return_none_for_invalid_length(self):
        """Test that normalize_cpf returns None for invalid length."""
        # Act
        result = normalize_cpf("123456789")  # Too short
        
        # Assert
        assert result is None
    
    def test_normalize_cpf_should_return_none_for_empty_string(self):
        """Test that normalize_cpf returns None for empty string."""
        # Act
        result = normalize_cpf("")
        
        # Assert
        assert result is None


class TestNormalizeCrm:
    """Tests for normalize_crm function."""
    
    def test_normalize_crm_should_format_with_crm_prefix(self):
        """Test that normalize_crm formats with CRM prefix."""
        # Act
        result = normalize_crm("CRM 12345 SP")
        
        # Assert
        assert result == "CRM 12345 SP"
    
    def test_normalize_crm_should_handle_without_state(self):
        """Test that normalize_crm handles CRM without state."""
        # Act
        result = normalize_crm("CRM 12345")
        
        # Assert
        assert result == "CRM 12345"
    
    def test_normalize_crm_should_handle_colon_separator(self):
        """Test that normalize_crm handles colon separator."""
        # Act
        result = normalize_crm("CRM: 12345")
        
        # Assert
        assert result == "CRM 12345"
    
    def test_normalize_crm_should_return_none_for_invalid_format(self):
        """Test that normalize_crm returns None for invalid format."""
        # Act
        result = normalize_crm("invalid crm")
        
        # Assert
        assert result is None


class TestNormalizePhone:
    """Tests for normalize_phone function."""
    
    def test_normalize_phone_should_format_10_digits(self):
        """Test that normalize_phone formats 10-digit phone."""
        # Act
        result = normalize_phone("1198765432")
        
        # Assert
        assert result == "(11) 9876-5432"
    
    def test_normalize_phone_should_format_11_digits(self):
        """Test that normalize_phone formats 11-digit phone (cell)."""
        # Act
        result = normalize_phone("11987654321")
        
        # Assert
        assert result == "(11) 98765-4321"
    
    def test_normalize_phone_should_handle_with_parentheses(self):
        """Test that normalize_phone handles phone with parentheses."""
        # Act
        result = normalize_phone("(11) 98765432")
        
        # Assert
        assert result == "(11) 9876-5432"
    
    def test_normalize_phone_should_return_none_for_invalid_length(self):
        """Test that normalize_phone returns None for invalid length."""
        # Act
        result = normalize_phone("12345")  # Too short
        
        # Assert
        assert result is None


class TestCleanText:
    """Tests for clean_text function."""
    
    def test_clean_text_should_remove_multiple_spaces(self):
        """Test that clean_text removes multiple spaces."""
        # Act
        result = clean_text("text   with    spaces")
        
        # Assert
        assert result == "text with spaces"
    
    def test_clean_text_should_trim_whitespace(self):
        """Test that clean_text trims whitespace."""
        # Act
        result = clean_text("  text  ")
        
        # Assert
        assert result == "text"
    
    def test_clean_text_should_handle_empty_string(self):
        """Test that clean_text handles empty string."""
        # Act
        result = clean_text("")
        
        # Assert
        assert result == ""
    
    def test_clean_text_should_handle_already_clean_text(self):
        """Test that clean_text handles already clean text."""
        # Act
        result = clean_text("clean text")
        
        # Assert
        assert result == "clean text"

